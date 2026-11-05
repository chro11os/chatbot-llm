# Learning Progress

## Pending decision
- Decision: how a reader finds where one record ends (CSE-1). Stage: awaiting reasoning.
- Awaited reply: the learner's approach after running the append snippet, given that text can contain any character, including newlines.

## Deferred decision
- Decision: CSE write flow (CSE-2, CSE-16). Stage: awaiting reasoning, deferred until the engine can append and read.
- Learner's proposal: the prompt is saved in the engine first, the API reads it from the engine, the frontend sends the Gemini reply back to the engine, and a parser converts engine contents to JSON for the API.
- Awaited reply: who writes each message to the engine, and what happens to a saved prompt if Gemini fails or the tab closes.

## CSE data flow
Introduced:
- A browser cannot call the C++ library directly; the library runs inside the backend process.
- Two formats: the log format on disk, and JSON over HTTP.

Demonstrated understanding:
- Learner proposed saving the prompt before calling Gemini, and identified that engine contents need converting for the API.

Needs reinforcement:
- Not yet assessed.
