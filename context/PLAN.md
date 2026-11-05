# Plan

## Trim the codebase to the bare minimum

Goal: keep only what the FastAPI backend and the Vite + React frontend need to run. Everything removed stays in git history.

### Target layout

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
  context/              (CLAUDE.md, PLAN.md, PROGRESS.md)
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

### Step 1: Root junk
- [x] Delete `bun.lock` at the root. It was created by running `bun add` in the wrong folder (there is no root `package.json`). The real one is `frontend/bun.lock`.
- [x] Delete the empty `playground/` folder.
- [x] Untrack `.DS_Store` (`git rm --cached .DS_Store`). It's already in `.gitignore` but was committed before.

### Step 2: Python, pick one dependency file
- [x] Keep `pyproject.toml` + `uv.lock` (uv is the current standard). Move the real deps into it: `fastapi[standard]`, `httpx`, `python-dotenv`, `pydantic`.
- [x] Delete `requirements.txt`. (Its `asyncio` entry is the stdlib, not a package.)

### Step 3: Drop the old CLI (the web server replaces it) -- SKIPPED, keeping for now
- [ ] Delete `main.py`, `core/prompt.py`, `.vscode/launch.json` (only launches `main.py`).
- [ ] Remove `clear_memory` from `core/json_format.py` (only `prompt.py` used it).

### Step 4: Runtime data out of git -- SKIPPED, keeping for now
- [ ] Remove the `lastresponse.json` debug dump line from `providers/gemini.py`.
- [ ] Add `memory/` to `.gitignore` and `git rm --cached memory/*.json`.
- [ ] In `core/json_format.py`, create the folder if missing, before `.touch()`: `memory_directory.parent.mkdir(exist_ok=True)`.

### Step 5: Frontend scaffold leftovers
- [x] Delete `frontend/README.md`, `frontend/notes.txt`, `frontend/.gitignore` (root one already covers it).
- [x] Delete `frontend/src/App.css` (not imported; `index.css` already loads Tailwind).
- [x] Delete `frontend/src/assets/` (hero.png, react.svg, vite.svg are unused).
- [x] Delete `frontend/public/icons.svg`. Keep `public/favicon.svg` (used by `index.html`) or delete it together with its `<link>` line.

### Step 6: Verify
- [ ] `uv sync` then `uv run fastapi dev server.py` starts on :8000.
- [ ] `cd frontend && bun run dev`, send a message, check `memory/chatmemory.json` gets written.
- [ ] `cd frontend && bun run build` passes (catches broken imports).

## Render Gemini's Markdown replies

Gemini replies in Markdown (`**bold**`, `### heading`, `* list`). `ReplyScreen` shows it as raw text, so the symbols show up and the newlines collapse.

- [x] `cd frontend && bun add react-markdown @tailwindcss/typography`
- [x] `frontend/src/index.css`: add `@plugin "@tailwindcss/typography";` under the Tailwind import.
- [x] `frontend/src/components/replyscreen.tsx`: wrap the reply in `<div className="prose m-7"><Markdown>{reply}</Markdown></div>` (add `max-w-none` for full width).
- [ ] Check in the browser: headings, bold and lists render with no leftover `**` / `###`.

## Next up
- [ ] Guard `chatbox.tsx` against error responses: check `res.ok` before `res.json()`. Right now any backend error (500, 504) makes `res.json()` throw inside the form action and React unmounts the whole page (blank screen).
- [ ] Backend: catch Gemini errors other than timeouts (e.g. `httpx.HTTPStatusError`) in `/api/chat` so they return a clear status instead of a bare 500.
- [ ] `ui/button.tsx`: add `border` so `border-gray-300` actually shows.

## Chat storage engine architecture

Tickets live in MILESTONE.md. This section is the design they build on.

### What it replaces
- `add_to_history` (`core/json_format.py`) rewrites the whole file for every message, so a crash mid-write can lose all history.
- `chat` (`server.py`) saves the two messages of a turn separately, so a crash between them leaves a user message with no reply (CSE-2).
- `chat` is a plain `def`, so FastAPI runs it on a thread pool and concurrent requests can overwrite each other (CSE-12).
- `/api/history` reads the JSON file directly, skipping `json_format.py`, so CSE-16 has to change both.

### Layers

```
server.py / core/prompt.py       same calls as today
         |
core/json_format.py              same function names, new insides
         |  ctypes (bytes + lengths)
======== Python / C++ boundary ========
C API: extern "C" functions      thin: no logic, catches all exceptions
         |
Engine: class                    owns file descriptor, mutex, open/append/read/clear
         |             |
Record codec           OS calls
bytes <-> message      open, write, fsync, flock, ftruncate
+ checksum, no I/O     |
                 memory/<log file>
```

### Paths
- Write: encode record -> take lock -> write at end of file -> flush to disk -> release -> return success. Success only comes after the flush (CSE-7).
- Read: take lock -> scan from the start, decoding each record -> return all messages.
- Open: take process lock -> check file identity -> scan records -> handle a bad record. A torn final record (CSE-8) and middle-of-file damage (CSE-9) are decided separately.

### Rules
- Mutex for threads in one process (CSE-12), file lock for other processes (CSE-13). Both are needed.
- `ctypes` releases the GIL during calls, so threads really do enter the C++ code at the same time.
- No C++ exception may cross `extern "C"`: catch them and return error codes.
- Python holds the engine as an opaque handle (`void*`).
- Memory allocated in C++ is freed in C++, so read results need a matching free function.
- Text crosses the boundary as UTF-8 bytes plus a length.

### Open questions
- CSE-13 stops the CLI and server running together, and rules out `--workers 2`.
- `kill -9` doesn't prove `fsync` works, because the OS keeps data from a finished `write()`. Only power loss exercises it. On macOS look at `F_FULLFSYNC`.
- `valgrind` has no solid support on recent macOS, so CSE-5 may need AddressSanitizer plus `leaks`.

## Later (ideas, not started)
- Show a "thinking..." state while waiting for Gemini.
- Show the whole conversation instead of only the latest reply.
- Let `Button` / `TextBox` accept normal HTML props (`ComponentProps<'button'>`, `placeholder`, etc.).
- Error boundary so a crash shows a message instead of a blank page.
- Three-column harness UI.
