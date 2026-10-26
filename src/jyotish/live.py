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

A unit is "claim:<area>:<finding id>", "paragraph:<area>", "when:<area>", "analysis:<area>:<section>"
or "summary". Nothing here decides what passes: the narration loop does, with the same validator and
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
            if self.state.get(unit) == "removed":    # the replacement: shown afresh
                self.shown.pop(unit, None)
                self.state.pop(unit, None)
                self.verified.pop(unit, None)
            parts = sentences(text)
            if not done:
                parts = parts[:-1]                   # the last one may still be being written
            have = self.shown.setdefault(unit, [])
            if parts[:len(have)] != have:            # the writer's text changed under us: replace it
                self.shown[unit] = list(parts)
                self.state[unit] = "verifying"
                self.emit({"type": "unit", "unit": unit, "area": unit_area(unit), "kind": unit_kind(unit),
                           "sentences": list(parts)})
                return
            for i in range(len(have), len(parts)):
                have.append(parts[i])
                self.state[unit] = "verifying"
                self.emit({"type": "sentence", "unit": unit, "area": unit_area(unit), "kind": unit_kind(unit),
                           "i": i, "text": parts[i]})

    def text(self, unit: str, text: str) -> None:
        """The unit's whole text, as the loop validates it: shown if the stream did not show it."""
        self.stream(unit, text, True)

    def removed(self, unit: str, why: str) -> None:
        with self.lock:
            if self.state.get(unit) in ("removed", "accepted") or unit not in self.shown:
                return
            self.state[unit] = "removed"
            self.emit({"type": "removed", "unit": unit, "why": why})

    def accepted(self, unit: str) -> None:
        with self.lock:
            if self.state.get(unit) == "accepted":
                return
            self.state[unit] = "accepted"
            self.emit({"type": "accepted", "unit": unit})

    def draft_stream(self, skip: Callable[[str], bool], on_done: Callable[[str, str], None] | None = None):
        """A reader for one streamed draft (a ReadingDraft or a ClientDraft): each unit's text is
        shown as it is written, unless `skip(unit)` (a held unit); `on_done(unit, text)` is told each
        unit whose text closed (a list section's item by item is not: it is checked with the draft)."""
        names: dict[int, str] = {}
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
            if unit is None or skip(unit):
                return
            if listed:                              # a list section: its items so far, one text
                got = items.setdefault((path[1], path[3]), {})
                got[path[4]] = value
                self.stream(unit, " ".join(got[k].strip() for k in sorted(got) if got[k].strip()), False)
                return
            self.stream(unit, value, done)
            if done and on_done is not None:
                on_done(unit, value)

        reader = JsonStrings(on_string)

        def feed(piece: str | None) -> None:
            if piece is None:
                names.clear(), fids.clear(), items.clear()
            reader.feed(piece)
        return feed

    def area_done(self, area: str, gaps: list[str]) -> None:
        self.emit({"type": "area", "area": area, "gaps": gaps})

    # the checks: started as soon as a unit is complete, their verdicts shown as they come
    def watch(self, unit: str, sentence: str, data: str) -> Future | None:
        """Start (or find) the check of one sentence of a unit; its verdict is shown when it comes."""
        if self.checker is None:
            return None
        fut, new = self.checker.submit(sentence, data)
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
            if all(p.supported for p in result.propositions):
                idx = [i for i, x in enumerate(shown) if x == sentence or sentence.startswith(x) or x in sentence]
                if unit_kind(unit) == "claim":
                    idx = list(range(len(shown)))      # a claim is checked whole
                for i in idx:
                    if i not in self.verified.setdefault(unit, set()):
                        self.verified[unit].add(i)
                        self.emit({"type": "verified", "unit": unit, "i": i})
            else:
                self.state[unit] = "removed"
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
        self.futures: dict[tuple[str, str], Future] = {}
        self.lock = threading.Lock()
        self.last_meta = None
        for attr in ("model", "effort", "backend", "config"):
            if hasattr(inner, attr):
                setattr(self, attr, getattr(inner, attr))

    def _one(self, sentence: str, data: str):
        ask = getattr(self.inner, "ask_one", None)
        if ask is not None:
            return ask(sentence, data)
        return self.inner(sentence, data), getattr(self.inner, "last_meta", None)

    def submit(self, sentence: str, data: str) -> tuple[Future, bool]:
        with self.lock:
            key = (sentence, data)
            fut = self.futures.get(key)
            if fut is not None:
                return fut, False
            fut = self.futures[key] = self.pool.submit(self._one, sentence, data)
            return fut, True

    def check_many(self, items: list[tuple[str, str]]):
        futs = [self.submit(s, d)[0] for s, d in items]
        out = [f.result() for f in futs]
        with self.lock:                     # a verdict is used once: a sentence sent again is checked again
            for s, d in items:
                self.futures.pop((s, d), None)
        return out

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
            while len(self.logs) > self.keep:
                self.logs.pop(next(iter(self.logs)))
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
