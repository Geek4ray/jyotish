"""The narration as it is written and checked (2026-10-26; docs/spec_notes_2026-10-26.md).

Three pieces. `JsonStrings` reads a structured draft as the writer streams it and reports each string
field, by its path in the draft, as it grows and when it closes. `Live` turns those strings into a
unit's sentences on the page and the checker's verdicts into their states: a sentence is shown
"being verified" while its unit waits on the validator and the checker, "verified" once the checker
passed it, and the unit is removed when either refuses it (the writer's replacement then streams in
the same way). It also starts each unit's checks as soon as the unit's text is complete, on a pool
shared by every area (`SharedChecker`), so the attempt's check step finds them done or in flight.
`LiveLog` keeps each reading's events in memory, numbered, for the server-sent events and the
polling fallback of the API.

The events, each a dict with `type`:
  sentence  {unit, area, kind, i, text}  a sentence of the unit, shown being verified
  unit      {unit, area, kind, sentences} the unit's sentences replaced (a draft not streamed, a reset)
  verified  {unit, i}                    the checker passed sentence i
  removed   {unit, why}                  the validator or the checker refused the unit
  accepted  {unit}                       every sentence of the unit passed: it is in the reading
  area      {area, gaps}                 the area's narration is finished (gaps: units that never passed)
  done      {}                           the reading is finished and stored

A unit is "claim:<area>:<finding id>", "paragraph:<area>:<key>" (one sentence of the paragraph, held on
its own since 2026-10-31: `HeldParagraph`), "when:<area>", "analysis:<area>:<section>" or "summary". Nothing here decides what passes: the narration loop does, with the same validator and
checker as before; this module only shows its decisions sooner."""

from __future__ import annotations

import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Callable

Event = dict[str, Any]


# --- reading a streamed JSON draft --------------------------------------------------------------

class JsonStrings:
    """An incremental reader of one JSON object: `feed(text)` with each piece as it arrives;
    `on_string(path, value, done)` is told every string value's text so far (done False) and when it
    closes (done True). A path is a tuple of keys and list indices. `feed(None)` starts again (a
    request sent again after a dropped stream)."""

    def __init__(self, on_string: Callable[[tuple, str, bool], None]):
        self.on_string = on_string
        self.reset()

    def reset(self) -> None:
        self.stack: list[list] = []          # frames: [kind "o"|"a", key or index, expecting "key"|"value"]
        self.mode = "value"                  # value | string | key | escape | unicode | literal | colon | after
        self.buf: list[str] = []
        self.key_buf: list[str] = []
        self.uni = ""
        self.in_key = False
        self.started = False

    def _path(self) -> tuple:
        return tuple(f[1] for f in self.stack)

    def feed(self, text: str | None) -> None:
        if text is None:
            self.reset()
            return
        grew = False
        for ch in text:
            grew |= self._char(ch)
        if grew and self.mode in ("string", "escape", "unicode") and not self.in_key:
            self.on_string(self._path(), "".join(self.buf), False)

    def _value_done(self) -> None:
        self.mode = "after"

    def _char(self, ch: str) -> bool:
        """One character; True when a value string grew."""
        m = self.mode
        if m in ("string", "escape", "unicode"):
            target = self.key_buf if self.in_key else self.buf
            if m == "escape":
                if ch == "u":
                    self.mode, self.uni = "unicode", ""
                    return False
                target.append({"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f"}.get(ch, ch))
                self.mode = "string"
                return not self.in_key
            if m == "unicode":
                self.uni += ch
                if len(self.uni) == 4:
                    try:
                        target.append(chr(int(self.uni, 16)))
                    except ValueError:
                        pass
                    self.mode = "string"
                    return not self.in_key
                return False
            if ch == "\\":
                self.mode = "escape"
                return False
            if ch == '"':
                if self.in_key:
                    self.stack[-1][1] = "".join(self.key_buf)
                    self.in_key, self.mode = False, "colon"
                else:
                    self.on_string(self._path(), "".join(self.buf), True)
                    self._value_done()
                return False
            target.append(ch)
            return not self.in_key
        if ch.isspace():
            if m == "literal":
                self._value_done()
            return False
        if m == "literal":
            if ch in ",}]":
                self._value_done()
                return self._char(ch)
            return False
        if m == "colon":
            if ch == ":":
                self.mode = "value"
            return False
        if m == "key":                        # inside an object, before a key
            if ch == '"':
                self.in_key, self.key_buf, self.mode = True, [], "string"
            elif ch == "}":
                self._close()
            return False
        if m == "value":
            if ch == "{":
                self.stack.append(["o", None])
                self.mode = "key"
            elif ch == "[":
                self.stack.append(["a", 0])
                self.mode = "value"
            elif ch == "]" and self.stack and self.stack[-1][0] == "a":
                self._close()                # an empty list
            elif ch == '"':
                self.buf, self.mode = [], "string"
            else:
                self.mode = "literal"
            return False
        if m == "after":
            if ch == ",":
                if self.stack and self.stack[-1][0] == "a":
                    self.stack[-1][1] += 1
                    self.mode = "value"
                else:
                    self.mode = "key"
            elif ch in "}]":
                self._close()
            return False
        return False

    def _close(self) -> None:
        if self.stack:
            self.stack.pop()
        self.mode = "after"


# --- the sentences of a unit and their states ---------------------------------------------------

def mark_of(sentence: str) -> str | None:
    """What the checker cannot pass in a sentence (review R3): a [tradition:] sentence is never checked,
    and a judgement's weighing is the reading's own (its premises are checked)."""
    from .narrate import TRADITION, is_judgement
    if TRADITION.search(sentence):
        return "tradition"
    return "judgement" if is_judgement(sentence) else None


class HeldParagraph:
    """A paragraph held sentence by sentence (2026-10-31; docs/spec_notes_2026-10-31.md): each sentence
    is a unit with a key, held once it passes the validator and the checker, and a retry rewrites only
    the failed ones. The first draft's sentences take the keys "1", "2", …; a retry's j-th sentence
    takes the j-th open key (a failed sentence's, in their order), and any beyond those follow the last
    open key as "<key>.1", "<key>.2", … (in the paragraph's order, `order`). A sentence the retry sends
    again verbatim beside the held ones is not placed. After the last attempt the held sentences stand
    as the paragraph, in their order; a key still open is the paragraph's gap."""

    def __init__(self):
        self.slots: dict[str, str] = {}             # key -> its latest sentence
        self.held: set[str] = set()
        self.errors: dict[str, list[str]] = {}      # key -> why its latest sentence failed

    @staticmethod
    def order(key: str) -> tuple[int, ...]:
        return tuple(int(x) for x in key.split("."))

    def keys(self) -> list[str]:
        return sorted(self.slots, key=self.order)

    def open(self) -> list[str] | None:
        """The keys a draft's sentences fill, in order; None before any sentence was placed."""
        return [k for k in self.keys() if k not in self.held] if self.slots else None

    def key(self, j: int, open_: list[str] | None) -> str:
        if open_ is None:
            return str(j + 1)
        if j < len(open_):
            return open_[j]
        base = open_[-1] if open_ else self.keys()[-1]
        return f"{base}.{j - len(open_) + 1}"

    def fresh(self, parts: list[str]) -> list[str]:
        """A draft's sentences less those that repeat a held one."""
        have = {self.slots[k] for k in self.held}
        return [p for p in parts if p not in have]

    def place(self, text: str | None) -> list[tuple[str, str]]:
        """This draft's sentences placed: (key, sentence) for each, to validate and check."""
        from .narrate import sentences
        open_ = self.open()
        if open_ == []:                              # every sentence is held: what the writer sent is ignored
            return []
        out = [(self.key(j, open_), s) for j, s in enumerate(self.fresh(sentences(text or "")))]
        for k, s in out:
            self.slots[k] = s
            self.errors.pop(k, None)
        return out

    def hold(self, key: str) -> None:
        self.held.add(key)
        self.errors.pop(key, None)

    def fail(self, key: str, why: list[str]) -> None:
        self.errors[key] = list(why)

    def text(self) -> str | None:
        """The held sentences, in their order; None when none is held."""
        held = [self.slots[k] for k in self.keys() if k in self.held]
        return " ".join(held) if held else None

    def failed(self) -> list[tuple[int, str, str, list[str]]]:
        """(position from 1, key, sentence, why) for each sentence not held."""
        return [(i, k, self.slots[k], self.errors.get(k, ["not checked"]))
                for i, k in enumerate(self.keys(), 1) if k not in self.held]

    def complete(self) -> bool:
        return bool(self.slots) and not self.failed()


def unit_kind(unit: str) -> str:
    return unit.split(":")[0]


def unit_area(unit: str) -> str | None:
    parts = unit.split(":")
    return parts[1] if len(parts) > 1 else None


class Live:
    """One reading's live view. `emit(event)` receives every event (the API's LiveLog); `t0` is the
    reading's start (time.perf_counter), from which the timeline is measured. Thread-safe: the areas
    are written in threads of their own."""

    def __init__(self, emit: Callable[[Event], None], t0: float | None = None):
        self._emit = emit
        self.t0 = t0 if t0 is not None else time.perf_counter()
        self.lock = threading.RLock()
        self.shown: dict[str, list[str]] = {}       # unit -> the sentences on the page
        self.state: dict[str, str] = {}             # unit -> verifying | accepted | removed
        self.verified: dict[str, set[int]] = {}
        self.removed_as: dict[str, list[str]] = {}    # unit -> the sentences it was removed with
        self.timeline: dict[str, float] = {}
        self.checker: "SharedChecker | None" = None

    def mark(self, name: str) -> None:
        with self.lock:
            self.timeline.setdefault(name, round(time.perf_counter() - self.t0, 3))

    def emit(self, event: Event) -> None:
        if event["type"] == "sentence":
            self.mark("first_sentence_s")
        elif event["type"] == "verified":
            self.mark("first_verified_s")
        elif event["type"] == "area":
            self.mark("first_area_s")
        self._emit(event)

    # the stream: sentences as they are written
    def stream(self, unit: str, text: str, done: bool) -> None:
        """A unit's text so far: every sentence that is complete (followed by more text, or the text is
        done) is shown, being verified. A unit already accepted is not shown again."""
        from .narrate import sentences
        with self.lock:
            if self.state.get(unit) == "accepted":
                return
            parts = sentences(text)
            if not done:
                parts = parts[:-1]                   # the last one may still be being written
            if self.state.get(unit) == "removed":
                # The text it was removed with, seen again (the loop validating the draft after the verdict
                # came, or a retry sending it unchanged), is not shown again; a different text is the
                # replacement, shown afresh.
                old = self.removed_as.get(unit, [])
                if parts == old[:len(parts)] and (not done or parts == old):
                    return
                self.shown.pop(unit, None)
                self.state.pop(unit, None)
                self.verified.pop(unit, None)
            have = self.shown.setdefault(unit, [])
            if parts[:len(have)] != have:            # the writer's text changed under us: replace it
                self.shown[unit] = list(parts)
                self.state[unit] = "verifying"
                self.emit({"type": "unit", "unit": unit, "area": unit_area(unit), "kind": unit_kind(unit),
                           "sentences": list(parts), "marks": [mark_of(x) for x in parts]})
                return
            for i in range(len(have), len(parts)):
                have.append(parts[i])
                self.state[unit] = "verifying"
                self.emit({"type": "sentence", "unit": unit, "area": unit_area(unit), "kind": unit_kind(unit),
                           "i": i, "text": parts[i], "mark": mark_of(parts[i])})

    def text(self, unit: str, text: str) -> None:
        """The unit's whole text, as the loop validates it: shown if the stream did not show it."""
        self.stream(unit, text, True)

    def removed(self, unit: str, why: str) -> None:
        with self.lock:
            if self.state.get(unit) in ("removed", "accepted") or unit not in self.shown:
                return
            self.state[unit] = "removed"
            self.removed_as[unit] = list(self.shown.get(unit, []))
            self.emit({"type": "removed", "unit": unit, "why": why})

    def withdraw(self, unit: str, why: str) -> None:
        """A unit's text taken back without a verdict (its stream restarted, or the loop never decided on
        it): removed from the page and forgotten, so the same text may be shown again (review R8)."""
        with self.lock:
            if self.state.get(unit) != "verifying":
                return
            self.emit({"type": "removed", "unit": unit, "why": why})
            for d in (self.shown, self.state, self.verified, self.removed_as):
                d.pop(unit, None)

    def sweep(self, prefixes: tuple[str, ...], why: str = "not in the writer's draft") -> None:
        """After an attempt's decisions: every unit of these prefixes still being verified was never decided
        on (an unknown finding id, a unit missing from the parsed draft); it is withdrawn (review R8)."""
        with self.lock:
            for unit in [u for u, st in self.state.items() if st == "verifying" and u.startswith(prefixes)]:
                self.withdraw(unit, why)

    def accepted(self, unit: str) -> None:
        with self.lock:
            if self.state.get(unit) == "accepted":
                return
            if self.state.get(unit) == "removed":    # passed on a later check of the same text: shown again
                again = self.removed_as.get(unit, [])
                self.shown[unit] = list(again)
                self.emit({"type": "unit", "unit": unit, "area": unit_area(unit), "kind": unit_kind(unit),
                           "sentences": again, "marks": [mark_of(x) for x in again]})
            self.state[unit] = "accepted"
            # The sentences the checker passed: every one but a [tradition:] sentence, which is never checked.
            shown = self.shown.get(unit, [])
            self.emit({"type": "accepted", "unit": unit,
                       "verified": [i for i, x in enumerate(shown) if mark_of(x) != "tradition"]})

    def draft_stream(self, skip: Callable[[str], bool], on_done: Callable[[str, str], None] | None = None,
                     paragraphs: dict[str, HeldParagraph] | None = None):
        """A reader for one streamed draft (a ReadingDraft or a ClientDraft): each unit's text is
        shown as it is written, unless `skip(unit)` (a held unit); `on_done(unit, text)` is told each
        unit whose text closed (a list section's item by item is not: it is checked with the draft).
        With `paragraphs` (area -> HeldParagraph), a paragraph streams sentence by sentence, each as
        "paragraph:<area>:<key>" under the key its draft will be placed at."""
        from .narrate import sentences
        names: dict[int, str] = {}
        opened: dict[str, list[str] | None] = {}    # area -> the paragraph's open keys as this draft began
        fids: dict[tuple[int, int], str] = {}
        items: dict[tuple[int, str], dict[int, str]] = {}

        def unit_of(path: tuple) -> tuple[str | None, bool]:
            if path == ("summary",):
                return "summary", False
            if len(path) < 3 or path[0] != "areas" or path[1] not in names:
                return None, False
            i, name = path[1], names[path[1]]
            if path[2] == "claims" and len(path) == 5 and path[4] == "text":
                fid = fids.get((i, path[3]))
                return (f"claim:{name}:{fid}" if fid else None), False
            if path[2] in ("paragraph", "when") and len(path) == 3:
                return f"{path[2]}:{name}", False
            if path[2] == "analysis" and len(path) >= 4:
                return f"analysis:{name}:{path[3]}", len(path) == 5
            return None, False

        def on_string(path: tuple, value: str, done: bool) -> None:
            if len(path) == 3 and path[0] == "areas" and path[2] == "name":
                if done:
                    names[path[1]] = value
                return
            if len(path) == 5 and path[0] == "areas" and path[2] == "claims" and path[4] == "finding_id":
                if done:
                    fids[(path[1], path[3])] = value
                return
            unit, listed = unit_of(path)
            if unit is not None and paragraphs is not None and unit.startswith("paragraph:"):
                held = paragraphs.setdefault(unit[10:], HeldParagraph())
                open_ = opened.setdefault(unit[10:], held.open())
                if open_ == []:
                    return
                parts = held.fresh(sentences(value))
                for j, part in enumerate(parts):
                    closed = done or j < len(parts) - 1
                    if not closed:
                        break                       # the last one may still be being written
                    piece = f"{unit}:{held.key(j, open_)}"
                    if not skip(piece) and piece not in closed_pieces:
                        closed_pieces.add(piece)
                        feed.stream(piece, part, True)
                        if on_done is not None:
                            on_done(piece, part)
                return
            if unit is None or skip(unit):
                return
            if listed:                              # a list section: its items so far, one text
                got = items.setdefault((path[1], path[3]), {})
                got[path[4]] = value
                feed.stream(unit, " ".join(got[k].strip() for k in sorted(got) if got[k].strip()), False)
                return
            feed.stream(unit, value, done)
            if done and on_done is not None:
                on_done(unit, value)

        reader = JsonStrings(on_string)
        seen: set[str] = set()                      # the units this stream showed
        closed_pieces: set[str] = set()             # the paragraph sentences this stream closed

        def stream_seen(unit: str, text: str, done: bool) -> None:
            seen.add(unit)
            self.stream(unit, text, done)

        def feed(piece: str | None) -> None:
            if piece is None:                       # the stream starts again: what it showed is withdrawn (R8)
                for unit in list(seen):
                    self.withdraw(unit, "the stream started again")
                seen.clear(), names.clear(), fids.clear(), items.clear(), closed_pieces.clear(), opened.clear()
            reader.feed(piece)
        feed.stream = stream_seen
        return feed

    def area_done(self, area: str, gaps: list[str]) -> None:
        self.emit({"type": "area", "area": area, "gaps": gaps})

    # the checks: started as soon as a unit is complete, their verdicts shown as they come
    def watch(self, unit: str, sentence: str, data: str) -> Future | None:
        """Start (or find) the check of one sentence of a unit; its verdict is shown when it comes."""
        if self.checker is None:
            return None
        fut, new = self.checker.submit(sentence, data, owner=unit_area(unit))
        if new or (unit, sentence) not in getattr(fut, "_watched", set()):
            watched = getattr(fut, "_watched", set())
            watched.add((unit, sentence))
            fut._watched = watched
            fut.add_done_callback(lambda f, u=unit, s=sentence: self._verdict(u, s, f))
        return fut

    def _verdict(self, unit: str, sentence: str, fut: Future) -> None:
        try:
            result, _ = fut.result()
        except Exception:                              # noqa: BLE001 - the loop reports it
            return
        with self.lock:
            if self.state.get(unit) != "verifying":
                return
            shown = self.shown.get(unit, [])
            # The verdict is for the text it was asked about: a late one for a text since replaced is dropped.
            if unit_kind(unit) == "claim":            # a claim is checked whole
                idx = list(range(len(shown))) if shown and all(x in sentence for x in shown) else []
            else:                                    # the sentence checked, exactly (review R8)
                idx = [i for i, x in enumerate(shown) if x == sentence]
            if not idx:
                return
            if all(p.supported for p in result.propositions):
                for i in idx:
                    if i not in self.verified.setdefault(unit, set()):
                        self.verified[unit].add(i)
                        self.emit({"type": "verified", "unit": unit, "i": i})
            else:
                self.state[unit] = "removed"
                self.removed_as[unit] = list(shown)
                self.emit({"type": "removed", "unit": unit, "why": "the checker"})


class NoLive:
    """No one is watching: every call is a no-op (the CLI, a replay)."""
    checker = None

    def __getattr__(self, name):
        return lambda *a, **k: None


# --- the checks of every area on one pool -------------------------------------------------------

class SharedChecker:
    """The checker of a reading whose areas are written in parallel: one pool of `concurrency`
    threads for every area's checks (the provider's limit is the reading's, not each area's), each
    (sentence, data) asked once. `check_many` is the narration loop's call: it returns the verdicts
    in the order asked, waiting on checks the stream already started."""

    def __init__(self, inner, concurrency: int):
        self.inner = inner
        self.concurrency = max(1, concurrency)
        self.pool = ThreadPoolExecutor(max_workers=self.concurrency, thread_name_prefix="check")
        self.futures: dict[tuple, Future] = {}
        self.lock = threading.Lock()
        self.runs: list[tuple[str, Any, Any, str | None]] = []    # every check asked: (sentence, result, meta, owner)
        self.used: set[int] = set()                               # ids of the runs a loop consumed
        self.last_meta = None
        for attr in ("model", "effort", "backend", "config"):
            if hasattr(inner, attr):
                setattr(self, attr, getattr(inner, attr))

    def _one(self, sentence: str, data: str, owner: str | None):
        ask = getattr(self.inner, "ask_one", None)
        result, meta = ask(sentence, data) if ask is not None else (self.inner(sentence, data),
                                                                  getattr(self.inner, "last_meta", None))
        with self.lock:
            self.runs.append((sentence, result, meta, owner))
        return result, meta

    def submit(self, sentence: str, data: str, owner: str | None = None) -> tuple[Future, bool]:
        """The check of (sentence, data) for `owner` (an area; checks are not shared across areas, so what
        the stream shows is the verdict that area's loop decides on)."""
        with self.lock:
            key = (owner, sentence, data)
            fut = self.futures.get(key)
            if fut is not None:
                return fut, False
            fut = self.futures[key] = self.pool.submit(self._one, sentence, data, owner)
            return fut, True

    def check_many(self, items: list[tuple[str, str]], owners: list[str | None] | None = None):
        """The loop's checks, each for its unit's area (`owners`, as Live.watch keys them)."""
        owners = owners or [None] * len(items)
        futs = [self.submit(s, d, o)[0] for (s, d), o in zip(items, owners)]
        out = [f.result() for f in futs]
        with self.lock:                     # a verdict is used once: a sentence sent again is checked again
            for (s, d), o in zip(items, owners):
                self.futures.pop((o, s, d), None)
            self.used.update(id(result) for result, _ in out)
        return out

    def unused(self) -> list[tuple[str, Any, Any, str | None]]:
        """Checks that ran and that no loop consumed (an early check of a unit the loop then dropped): real
        calls, counted in the reading's usage and kept in the recording (review R8)."""
        with self.lock:
            return [r for r in self.runs if id(r[1]) not in self.used]

    def __call__(self, sentence: str, data: str):
        result, self.last_meta = self.check_many([(sentence, data)])[0]
        return result

    def close(self) -> None:
        self.pool.shutdown(wait=False, cancel_futures=True)


# --- the events of every reading the service is writing ----------------------------------------

class LiveLog:
    """Each reading's events in memory, numbered from 1 (`version`), for GET /readings/{id}/events
    (server-sent events) and GET /readings/{id}/live?since=N (the polling fallback). A process
    keeps the last `keep` readings' logs; a reading whose log is gone is read from its stored
    document, which is complete once the reading is done."""

    def __init__(self, keep: int = 200):
        self.keep = keep
        self.logs: dict[str, list[Event]] = {}
        self.cond = threading.Condition()

    def append(self, reading_id: str, event: Event) -> int:
        with self.cond:
            log = self.logs.setdefault(reading_id, [])
            log.append(dict(event, seq=len(log) + 1))
            # Only a finished reading's log is evicted; a running one keeps its numbering (review R8).
            finished = [k for k, v in self.logs.items() if v and v[-1]["type"] == "done" and k != reading_id]
            while len(self.logs) > self.keep and finished:
                self.logs.pop(finished.pop(0))
            self.cond.notify_all()
            return len(log)

    def writer(self, reading_id: str) -> Callable[[Event], None]:
        return lambda e: self.append(reading_id, e)

    def since(self, reading_id: str, n: int) -> tuple[list[Event], int, bool]:
        with self.cond:
            log = self.logs.get(reading_id, [])
            return list(log[n:]), len(log), bool(log) and log[-1]["type"] == "done"

    def known(self, reading_id: str) -> bool:
        with self.cond:
            return reading_id in self.logs

    def wait(self, reading_id: str, n: int, timeout: float) -> tuple[list[Event], int, bool]:
        with self.cond:
            self.cond.wait_for(lambda: len(self.logs.get(reading_id, [])) > n, timeout=timeout)
        return self.since(reading_id, n)
