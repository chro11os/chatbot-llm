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
