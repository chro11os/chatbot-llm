# CLAUDE.md

## Working rules

> **Paused 2026-11-13:** at my request Claude writes all the code directly (frontend, backend, CSE). The rules below are kept for when I switch learning back on.

### Working mode: snippet generator only

- Do NOT edit, create, or delete files in this project. Reply with code snippets in chat; I paste them in myself.
- Exception: Claude owns the frontend UI and edits files under `frontend/` directly. I'm focusing on the backend and CSE, where the snippet rule still applies.
- Don't run commands that change anything (installs, formatters, git, scripts that write files). Read-only looks are fine if you need context.
- Keep snippets small and focused on what I asked for. No full-file rewrites unless I ask.
- Always give me the minimal snippet or code I'm asking for, doesnt have to be a polished code that thinks about all the cases and edge cases. I want something that works minimally.
- Say where a snippet goes (file + function/line) when it isn't obvious.

### I'm learning, but I want room to build

- Explain what I'm looking at: what the code does and how the pieces connect.
- You can give me the fix, but every fix must come with:
  1. **Why the problem happens**: the root cause, not just the symptom.
  2. **What the fix does**: how it solves the cause, line by line if needed.
- Don't rewrite or refactor beyond what the fix needs. If you spot other issues, mention them separately and let me decide.
- Name the concepts involved and point me to the relevant docs so I can dig deeper.
- When generating code explain what a codeblock or a snippet does.

### Id like to be asked if i have any questions

- When generating code, or other concepts ask me if i have any other questions, give me options of possible questions i might have.

### Context

- Write the plans we make or have under Plan in this file.
- Write the progress of the app under Progress in this file (get the context of the progress from the plan).
- Always trim finished plans: once a plan's items are done, record them under Progress and remove them from Plan. Git keeps the history.
- CSE tickets stay in `context/MILESTONE.md`.

## Chat storage engine instructions

Applies to everything in `cse/` and the tickets in `context/MILESTONE.md`.

- Give me the architecture and snippets for the CSE, not the whole code.
- C++ snippets use generic code, not functional code for this project. Use unrelated names like `Widget` and show one technique at a time.
- The goal is that I don't get answers easily and I build a mental pathway.
- It should feel like I'm looking through Stack Overflow while building this: I adapt the idea to my own code.
- Base architecture on the existing code. Read the codebase first.
- Leave the design decisions in the tickets to me.

## Plan

### Trim the codebase to the bare minimum

Goal: keep only what the FastAPI backend and the Vite + React frontend need to run. Everything removed stays in git history.

#### Target layout

```
chatbot-llm/
  .gitignore
  .env                  (ignored)
  README.md
  pyproject.toml
  uv.lock
  server.py
  core/json_format.py
  providers/gemini.py
  memory/               (runtime data, ignored by git)
  CLAUDE.md
  context/              (MILESTONE.md)
  frontend/
    index.html
    package.json
    bun.lock
    vite.config.ts
    eslint.config.js
    tsconfig.json, tsconfig.app.json, tsconfig.node.json
    src/main.tsx, src/App.tsx, src/index.css
    src/components/chatbox.tsx, src/components/replyscreen.tsx
```

#### Step 3: Drop the old CLI (the web server replaces it) -- SKIPPED, keeping for now
- [ ] Delete `main.py`, `core/prompt.py`, `.vscode/launch.json` (only launches `main.py`).
- [ ] Remove `clear_memory` from `core/json_format.py` (only `prompt.py` used it).

#### Step 4: Runtime data out of git -- SKIPPED, keeping for now
- [ ] Remove the `lastresponse.json` debug dump line from `providers/gemini.py`.
- [ ] Add `memory/` to `.gitignore` and `git rm --cached memory/*.json`.
- [ ] In `core/json_format.py`, create the folder if missing, before `.touch()`: `memory_directory.parent.mkdir(exist_ok=True)`.

#### Step 6: Verify
- [ ] `uv sync` then `uv run fastapi dev server.py` starts on :8000.
- [ ] `cd frontend && bun run dev`, send a message, check `memory/chatmemory.json` gets written.
- [ ] `cd frontend && bun run build` passes (catches broken imports).

### Render Gemini's Markdown replies

- [ ] Check in the browser: headings, bold and lists render with no leftover `**` / `###`.


### Later (ideas, not started)
- Let `Button` / `TextBox` accept normal HTML props (`ComponentProps<'button'>`, `placeholder`, etc.).
- Error boundary so a crash shows a message instead of a blank page.

## Progress

### 2026-11-03: Codebase trim (Plan steps 1, 2, 5)
- Done: removed stray root `bun.lock`, empty `playground/`, untracked `.DS_Store`.
- Done: Python deps now live only in `pyproject.toml` + `uv.lock` (fastapi[standard], httpx, python-dotenv, pydantic). `requirements.txt` removed.
- Done: removed frontend template leftovers (README, notes.txt, .gitignore, App.css, src/assets/, public/icons.svg).
- Skipped by choice: step 3 (CLI files) and step 4 (memory/ out of git).
- Verified: backend imports under `uv run`; `vite build` bundles fine.
- Open: `tsc -b` fails on `App.tsx` because `Chatbox` doesn't accept the `onReply` prop yet (the in-progress reply wiring, not caused by the trim).

### 2026-11-03: Frontend wired to backend
- Done: `Chatbox` takes an `onReply` prop, awaits `/api/chat`, and passes `data.reply` up to `App` (lifting state up). `tsc -b` passes again.
- Done: replies show in `ReplyScreen`; both turns save to `memory/chatmemory.json`. Verified in the browser.
- Done: Gemini timeout raised to 60s (`providers/gemini.py`); `/api/chat` returns a 504 instead of crashing on `httpx.TimeoutException` (`server.py`).
- How to run: `uv run fastapi dev server.py` (port 8000), and `bun run dev` in `frontend/` (port 5173, proxies `/api` to 8000). `uv run server.py` alone exits immediately because nothing starts a server.
- Next: render Markdown replies (see Plan).

### 2026-11-03: Markdown replies and UI components
- Done: Markdown rendering. `react-markdown` + `@tailwindcss/typography` installed in `frontend/`; `index.css` loads the plugin; `ReplyScreen` renders `<Markdown>` inside a `prose` div. Not yet checked in the browser with a long reply.
- Done: started `frontend/src/ui/` for reusable styled pieces:
  - `button.tsx`: real `<button>` that renders `children` (default `type="submit"` inside the form).
  - `text-box.tsx`: styled `<input name="text" required>`.
- Fixed: clicking the textbox blanked the page. Cause: `TextBox` was a `<button>` wrapping the input, so the click bubbled up and submitted an empty message; Gemini rejected it, the backend returned 500, `res.json()` threw, and React unmounted the app. Fix: `TextBox` is now the `<input>` itself, and `required` blocks empty submits.
- Cleanup: removed an accidental root `package.json` (bun belongs only in `frontend/`).
- Not committed yet: Markdown + `ui/` changes.
- Next: `res.ok` guard in `chatbox.tsx` (see "Next up" in Plan).

### 2026-11-12: Harness UI (Claude owns frontend/)
- Done: `App.tsx` is now three columns: History (from `/api/history`, refetched after each turn), Chat (the whole session conversation plus `Chatbox`), Debug (status, ms and raw body for each `/api/chat` call; red when it errors).
- Done: the fetch moved from `Chatbox` to `App.send`; `Chatbox` takes `onSend(text)`. Error responses show as a message instead of blanking the page (`res.ok` guard).
- Done: `ui/button.tsx` border shows.
- Verified: `tsc` + eslint are clean except `react-markdown` missing from `node_modules` (it's in package.json; run `bun install` in `frontend/`). Not checked in the browser yet.
- Done: loading state. The message shows in Chat straight away with a `thinking…` placeholder (`useOptimistic`); the textbox and button are disabled and the button reads `Sending…` while the request runs (`useFormStatus` + `<fieldset disabled>`).
- Done: `TextBox` is a `<textarea>` that grows with its content (`field-sizing-content`, 6–16rem). Enter sends, Shift+Enter adds a new line.
- Verified: `bun run build` + eslint pass. Not checked in the browser yet.
- Done: usage ring above the Send button (`components/usagering.tsx`). It fills toward an arbitrary 100k-token session budget; hovering shows session input/output/thought tokens and the last turn. It reads `body.usage` from each `/api/chat` reply, so it stays empty until the backend returns usage. Resets on page reload.
- Done: dark theme by default (`index.css` sets `color-scheme: dark` + dark body; `prose-invert` for Markdown; components recolored). No light mode yet.
- Done: resizable columns. `App.tsx` uses flex with a drag bar (`Handle`, pointer capture) between columns; side columns clamp to 200px–half the window, Chat takes the rest. Widths reset on reload.
- Done: pixel pet fixed bottom-right (`components/pet.tsx`, original sprite in Claude-ish orange, animations in `index.css`). It bobs and blinks; bobs faster with a `thinking…` bubble while a request runs. Click-through (`pointer-events-none`), still under reduced motion.

### 2026-11-13: Chat storage engine + backend finished (written by Claude)
- Engine: `cse/engine.cpp` builds to `cse/libcse.dylib` (command in README). Append-only log `memory/chat.log`: `"CSE1"` header, then records `[u32 len][u32 crc32][payload]`.
  - Append: encode, mutex (threads) + `flock` (processes), one `write()`, `F_FULLFSYNC`/`fsync`, then success. A failed write is truncated back off.
  - Open: a torn final record is cut off; a bad record with data after it makes open refuse (no guessing). Reads take a shared `flock`, so the CLI and server can run together.
  - C API (`extern "C"`, catches everything, returns 0/-1): `cse_open/append/read_all/free/clear/close`. Python holds a `void*`; read buffers are freed with `cse_free`.
- Python: `core/json_format.py` wraps it in `Log` via ctypes. One record = one JSON list of messages, so a turn (user + model) saves atomically (`add_turn`). `read_history()` backs `/api/history`. The old `memory/chatmemory.json` (32 messages) was imported once and renamed `chatmemory.json.imported`.
- Backend: `call_api` returns `(reply, usage)`; `/api/chat` returns `usage` (fills the usage ring) and maps Gemini HTTP errors to 502 with the detail. CLI: `/clear` and `/quit` no longer also send the command to Gemini.
- Verified: `uv run python cse/test_engine.py` passes (round trip, 8 threads x 50 appends, torn tail, mid-file damage, clear, `kill -9` mid-append). A real `/api/chat` call returned usage and saved the turn. `bun run build` passes.
- Not verified: power loss (the only true `fsync` test), memory leaks (`leaks`/ASan not run).
- Left alone: `cse/main.cpp` (your uncommitted practice code) and `cse/get_userinput.cpp`; `cse/userinput` is a tracked binary.
