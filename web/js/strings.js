// Every label of the guided review, in one place: a translation is one more block below
// (copy `en`, translate the values, keep the keys and the {placeholders}). The page picks the
// language from ?lang=, then the browser's; a key a translation lacks falls back to English.
// Words an astrologer would use: never the engine's own (its vote, test, family or checker).

export const STRINGS = {
  en: {
    "title": "Review",
    "title.blind": "Judge",
    "signin.heading": "Reviewer sign-in",
    "signin.token": "Reviewer token",
    "signin.open": "Open the reading",
    "signin.refused": "The reviewer token was not accepted.",
    "compare.title": "Compare two readings",
    "compare.open": "Open the two readings",
    "compare.lead": "Two readings of the same chart and question. How each was written is withheld until you answer.",
    "compare.reading": "Reading {label}",
    "compare.question": "Which reading would you give the client, and why?",
    "compare.choice": "Reading {label}",
    "compare.why": "Why, in your own words",
    "compare.submit": "Give my answer",
    "compare.both": "Choose a reading and say why.",
    "compare.revealed": "Your answer, and how each reading was written",
    "compare.you_chose": "You chose reading {label} ({reviewer}).",
    "compare.settings": "{model}, effort {effort}, depth {depth}",
    "chart.heading": "The chart",
    "chart.dasha": "Vimshottari",
    "chart.current": "Current period on {date}: {period}",
    "chart.maha": "Mahadasha",
    "chart.antar": "Antardasha in {maha}",
    "chart.from": "From",
    "chart.to": "To",
    "chart.now": "now",
    "chart.loading": "Drawing the chart…",
    "progress": "Step {n} of {total}",
    "nav.back": "Back",
    "nav.next": "Next",
    "nav.next_area": "Next area",
    "nav.begin": "Begin",
    "nav.keys": "Keys: 1, 2, 3 choose · Enter goes on",
    "nav.keys_text": "Ctrl+Enter goes on from a text box",
    "saved": "Saved",
    "saving": "Saving…",
    "save_failed": "Not saved: {message}",
    "choose_first": "Choose an answer first.",

    "intro.1.heading": "What the engine did",
    "intro.1.body": "The engine computed this chart exactly: positions, divisional charts, dashas, strengths. It found the combinations the classical texts name and weighed each house of the question from several directions. Then it wrote a short reading for each area in plain words, and a period for areas the question asks about.",
    "intro.2.heading": "What checked text means",
    "intro.2.body": "Every sentence of the reading was read back against the chart facts it rests on before it was shown. A sentence says only what the chart shows. If you rewrite one, your words are read back the same way: you will see the facts beside it, and if a rewrite goes beyond them you are told why in plain words.",
    "intro.3.heading": "Your note goes to the client",
    "intro.3.body": "For each area you may add a note. The client sees it as the astrologer's own words, under your name ({name}), set apart from the engine's text and not read back against the chart. Your other answers stay with us: they teach the engine and the client never sees them.",
    "intro.blind": "This is the blind reading: for each area you first answer from the chart alone. The engine's reading and its period appear only after.",

    "areaname.personality": "self",
    "areaname.wealth": "wealth",
    "areaname.siblings": "siblings",
    "areaname.mother_home": "home and mother",
    "areaname.children": "children",
    "areaname.intellect": "learning",
    "areaname.health": "health",
    "areaname.debts_enemies": "debts and adversaries",
    "areaname.marriage": "marriage",
    "areaname.longevity": "longevity",
    "areaname.father": "father",
    "areaname.fortune": "fortune",
    "areaname.career": "career",
    "areaname.gains": "gains",
    "areaname.foreign": "foreign",
    "areaname.spirituality": "spiritual life",
    "areaname.mind": "mind",
    "areaname.reputation": "reputation",
    "areaname.synastry": "synastry",
    "area.heading": "{area}",
    "area.of": "Area {n} of {total}",

    "blind_reading.q": "From the chart alone: how do you read it for {area}?",
    "blind_reading.promising": "Promising",
    "blind_reading.mixed": "Mixed",
    "blind_reading.difficult": "Difficult",
    "blind_period.q": "From the chart alone: which is the best period for {area}?",
    "blind_period.hint": "A range of months, as you would tell a client.",

    "match.lead": "The engine's reading for {area}",
    "match.q": "Does this match your reading of the chart for {area}?",
    "match.agree": "Agree",
    "match.partly": "Partly",
    "match.disagree": "Disagree",
    "match.your_blind": "Your reading from the chart alone: {answer}",
    "astro.toggle": "For the astrologer",
    "astro.sheet": "The technical sheet (the engine's figures, no model)",
    "astro.findings": "The findings, one by one",
    "astro.sheet_review": "The technical sheet for {area}: the engine's figures behind the paragraph",
    "print.label": "Print",
    "print.client": "The client's view",
    "print.both": "Both views",
    "print.go": "Print",
    "client.says": "What the chart says for you",
    "client.when": "When",
    "client.not_tell": "What this chart does not tell",
    "pending.notice": "The written analysis is being prepared; every engine field on this page is complete, and the checked text is added as it passes.",
    "pending.area": "The written analysis is being prepared.",
    "pending.engine_lines": "The engine's own lines (no model)",
    "gaps.summary": "Not written within the checks ({n}): what was refused, as the engine gave it",

    "off.q": "What is off?",
    "off.hint": "Choose all that apply.",
    "off.missing_combination": "A combination is missing",
    "off.weight": "The weight given to something",
    "off.timing": "The timing",
    "off.wording": "The wording",
    "off.other": "Something else",
    "off.line": "In a line (optional)",

    "sentences.q": "Anything to change?",
    "sentences.hint": "Keep a sentence as it is, or rewrite it in your words.",
    "sentences.keep": "Keep",
    "sentences.rewrite": "Rewrite",
    "sentences.facts": "What the chart shows for this sentence",
    "sentences.no_facts": "This sentence names no chart fact of its own.",
    "sentences.check": "Read it back and use it",
    "sentences.cancel": "Cancel",
    "sentences.checking": "Reading it back against the chart…",
    "sentences.accepted": "Accepted: the reading now says this.",
    "sentences.refused": "Not accepted:",
    "sentences.rewritten": "Rewritten",
    "sentences.none": "This area has no sentences to change.",

    "reason.unsupported": "The chart facts beside it do not show this: “{detail}”.",
    "reason.timing": "Leave out dates and periods (“{detail}”): the reading gives its period separately.",
    "reason.probability": "Leave out odds and chances (“{detail}”).",
    "reason.confidence": "Leave out words of certainty (“{detail}”).",
    "reason.death": "The reading never speaks of death or the length of life (“{detail}”).",
    "reason.medical": "Leave out medical words (“{detail}”).",
    "reason.trade": "Leave out advice to buy or sell.",
    "reason.third_party": "Do not say what another person will do (“{detail}”).",
    "reason.tier": "Leave out “{detail}”: how strong the area is, is stated separately.",
    "reason.name": "Name the combination this sentence is about: {detail}.",
    "reason.reference": "Each sentence is read on its own: leave out “{detail}”, which points to another.",
    "reason.other": "The sentence could not be tied to the chart facts it rests on.",

    "comment.label": "In your own words (optional)",
    "comment.hint": "Ctrl+Enter sends it with your answer. It stays with us: the client never sees it.",

    "whole.q": "Anything about the reading as a whole?",
    "whole.hint": "What the areas do not say on their own: the balance of the reading, what you would tell the client first. It stays with us.",
    "whole.label": "The reading as a whole",

    "note.q": "What would you add?",
    "note.hint": "The client sees this as the astrologer's own words, under your name. Leave it empty to add nothing.",
    "note.label": "Your note on {area}",

    "period.q": "Does the best period match yours?",
    "period.engine": "The engine's best period for {area}",
    "period.range": "{start} to {end}",
    "period.avoid": "Period to avoid: {start} to {end}",
    "period.yes": "Yes",
    "period.earlier": "Earlier",
    "period.later": "Later",
    "period.different": "A different period",
    "period.yours": "Your period",
    "period.your_blind": "Your period from the chart alone: {start} to {end}",
    "period.from": "From",
    "period.to": "To",
    "period.need_range": "Give the period as a range of months.",

    "summary.heading": "Your review",
    "summary.empty": "–",
    "summary.match": "Your reading",
    "summary.blind_reading": "From the chart alone",
    "summary.blind_period": "Your period from the chart alone",
    "summary.off": "What is off",
    "summary.sentences": "Sentences rewritten",
    "summary.note": "Your note",
    "summary.period": "Best period",
    "summary.approve": "Approve",
    "summary.approve_line": "The client will see: reviewed by {name}",
    "summary.edit": "Change an answer",
    "summary.change": "Change",
    "summary.whole": "The reading as a whole",
    "summary.words": "“{words}”",

    "done.heading": "Done",
    "done.body": "The reading is approved. The client sees it now, reviewed by {name}.",
    "done.client": "See the client's page",
    "done.already": "This reading was approved by {name}.",
  },
};

let lang = "en";

export function setLanguage(code) {
  lang = code && STRINGS[code] ? code : "en";
  document.documentElement.lang = lang;
}

export function pickLanguage() {
  const asked = new URLSearchParams(location.search).get("lang");
  const nav = (navigator.language || "en").slice(0, 2);
  setLanguage(asked || (STRINGS[nav] ? nav : "en"));
}

// The label for `key` with its {placeholders} filled.
export function t(key, vars = {}) {
  const s = (STRINGS[lang] && STRINGS[lang][key]) ?? STRINGS.en[key];
  if (s === undefined) throw new Error(`no string ${key}`);
  return s.replace(/\{(\w+)\}/g, (_, k) => (vars[k] ?? `{${k}}`));
}
