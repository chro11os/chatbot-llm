# Project Map

## Purpose
A chatbot: a React web page sends a message to a FastAPI backend, which gets a reply from Gemini and saves the turn to a JSON file. A C++ chat storage engine (CSE) is planned to replace that file.

## Requirements
- CSE goal (`context/MILESTONE.md`): crash-safe, append-only log; the chatbot behaves the same from the user's side; history survives `kill -9` during a write.
- CSE out of scope: multiple chats, an index, compaction, frontend changes.
- Working rules (`CLAUDE.md`): snippets only, the learner pastes code in; CSE help is architecture plus generic C++ only; CSE design decisions stay with the learner.

## Components
Implemented:
- Frontend: `frontend/src/App.tsx` (holds reply state), `components/chatbox.tsx` (form, posts to `/api/chat`), `components/replyscreen.tsx` (Markdown), `ui/button.tsx`, `ui/text-box.tsx`.
- Backend: `server.py` (`POST /api/chat`, `GET /api/history`).
- Gemini client: `providers/gemini.py` (`call_api`).
- Storage: `core/json_format.py` (`add_to_history`, `clear_memory`, `memory_directory`).
- CLI: `main.py`, `core/prompt.py`.

Started:
- CSE: `cse/main.cpp` (empty `main`), `cse/get_userinput.cpp` (input practice).

## Main Flow
Implemented:
chatbox.tsx --POST /api/chat--> server.py --call_api--> Gemini
server.py --add_to_history (twice)--> memory/chatmemory.json
server.py --reply--> chatbox.tsx --onReply--> App --> ReplyScreen

Planned in `CLAUDE.md`, not implemented:
core/json_format.py --ctypes--> extern "C" functions --> Engine class --> log file in memory/

## Data and Trust Boundaries
- History: `memory/chatmemory.json`, currently tracked by Git.
- Last raw Gemini response: `memory/lastresponse.json`.
- Secret: `GEMINI_API_KEY`, loaded from `.env`, which is ignored by Git.
- External service: Gemini API, called over HTTPS.
- Auth on the backend routes: none in the code.
- Gemini receives only the current message; saved history is not sent.

## Build and Deployment
- Backend: `uv run fastapi dev server.py` (port 8000).
- Frontend: `bun run dev` in `frontend/` (port 5173, proxies `/api` to 8000).
- Frontend build: `bun run build` in `frontend/`.
- CSE: no build configuration in the repo.
- Deployment: no configuration found in the repo.

## Unknowns
- CSE record format and file header (CSE-1).
- One record per turn or two (CSE-2).
- CSE-9 behaviour for middle-of-file damage.
- CSE build setup and where the shared library lives.
