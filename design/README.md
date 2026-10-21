# Design mockups

Four screens of the website, exported from the design canvas at
https://claude.ai/artifact/JV7Ytun1Qn3uSVF1gDujA9 (the living copy; edit there and re-export):

| file | screen |
| --- | --- |
| `mockups/Home.html` | landing: birth-data form, what the engine does and does not claim |
| `mockups/Main.html` | the reading, desktop: summary, areas with tier and stability, claims with citations, learner panel |
| `mockups/Timing.html` | a "when" answer: windows table, derivation, avoid window |
| `mockups/Phone.html` | the reading on a phone |

Plain HTML with inline styles (the canvas runtime script is removed). Palette: background
#0F1230, text #F3EEE2, accent #E8A33D, rule #2E3260; type Fraunces (display) and Inter (body).
The numbers on the mockups are illustrative; the page is built from the reading JSON
(`examples/reference_reading.json`, the SPEC output schema), never from these files.
