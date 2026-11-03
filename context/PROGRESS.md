# Progress

## 2026-11-03: Codebase trim (PLAN.md steps 1, 2, 5)
- Done: removed stray root `bun.lock`, empty `playground/`, untracked `.DS_Store`.
- Done: Python deps now live only in `pyproject.toml` + `uv.lock` (fastapi[standard], httpx, python-dotenv, pydantic). `requirements.txt` removed.
- Done: removed frontend template leftovers (README, notes.txt, .gitignore, App.css, src/assets/, public/icons.svg).
- Skipped by choice: step 3 (CLI files) and step 4 (memory/ out of git).
- Verified: backend imports under `uv run`; `vite build` bundles fine.
- Open: `tsc -b` fails on `App.tsx` because `Chatbox` doesn't accept the `onReply` prop yet (the in-progress reply wiring, not caused by the trim).

## 2026-11-03: Frontend wired to backend
- Done: `Chatbox` takes an `onReply` prop, awaits `/api/chat`, and passes `data.reply` up to `App` (lifting state up). `tsc -b` passes again.
- Done: replies show in `ReplyScreen`; both turns save to `memory/chatmemory.json`. Verified in the browser.
- Done: Gemini timeout raised to 60s (`providers/gemini.py`); `/api/chat` returns a 504 instead of crashing on `httpx.TimeoutException` (`server.py`).
- How to run: `uv run fastapi dev server.py` (port 8000), and `bun run dev` in `frontend/` (port 5173, proxies `/api` to 8000). `uv run server.py` alone exits immediately because nothing starts a server.
- Next: render Markdown replies (see PLAN.md).

## 2026-11-03: Markdown replies and UI components
- Done: Markdown rendering. `react-markdown` + `@tailwindcss/typography` installed in `frontend/`; `index.css` loads the plugin; `ReplyScreen` renders `<Markdown>` inside a `prose` div. Not yet checked in the browser with a long reply.
- Done: started `frontend/src/ui/` for reusable styled pieces:
  - `button.tsx`: real `<button>` that renders `children` (default `type="submit"` inside the form).
  - `text-box.tsx`: styled `<input name="text" required>`.
- Fixed: clicking the textbox blanked the page. Cause: `TextBox` was a `<button>` wrapping the input, so the click bubbled up and submitted an empty message; Gemini rejected it, the backend returned 500, `res.json()` threw, and React unmounted the app. Fix: `TextBox` is now the `<input>` itself, and `required` blocks empty submits.
- Cleanup: removed an accidental root `package.json` (bun belongs only in `frontend/`).
- Not committed yet: Markdown + `ui/` changes.
- Next: `res.ok` guard in `chatbox.tsx` (see PLAN.md "Next up").
