# Learning Progress

## Pending decision
- Decision: how a reader finds where one record ends (CSE-1). Stage: awaiting reasoning.
- Awaited reply: the learner's approach after running the append snippet, given that text can contain any character, including newlines.

## Deferred decision
- Decision: CSE write flow (CSE-2, CSE-16). Stage: awaiting reasoning, deferred until the engine can append and read.
- Learner's proposal: the prompt is saved in the engine first, the API reads it from the engine, the frontend sends the Gemini reply back to the engine, and a parser converts engine contents to JSON for the API.
- Awaited reply: who writes each message to the engine, and what happens to a saved prompt if Gemini fails or the tab closes.
- 2026-11-07: learner wants the engine to act as a database the frontend can pull from. Decided: reading the whole history is enough (no lookups/search). Explained: browser reaches the engine only through backend routes; frontend-sent replies could be forged. Still awaiting: who writes each message.
- 2026-11-07: learner deleted `context/MILESTONE.md` and `cse/append_bytes.cpp` (in git history).

## CSE data flow
Introduced:
- A browser cannot call the C++ library directly; the library runs inside the backend process.
- Two formats: the log format on disk, and JSON over HTTP.

Demonstrated understanding:
- Learner proposed saving the prompt before calling Gemini, and identified that engine contents need converting for the API.

Needs reinforcement:
- Not yet assessed.

## Scope change
- 2026-11-12: learner handed the frontend UI to Claude (edits files directly, no learning checkpoints there). Learning focus: backend and CSE. The CSE-1 pending decision is unchanged.
- 2026-11-13: learner asked Claude to finish the whole app, including the CSE, and confirmed the override. Learning paused. Claude made the CSE-1/2/8/9/13 design decisions (length+crc framing, one record per turn, cut torn tail / refuse mid-file damage, per-operation flock); these are Claude's decisions, not demonstrated learner reasoning. The CSE-1 pending decision is closed by that implementation.
