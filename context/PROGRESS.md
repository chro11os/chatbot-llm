# Progress

## 2026-11-03: Codebase trim (PLAN.md steps 1, 2, 5)
- Done: removed stray root `bun.lock`, empty `playground/`, untracked `.DS_Store`.
- Done: Python deps now live only in `pyproject.toml` + `uv.lock` (fastapi[standard], httpx, python-dotenv, pydantic). `requirements.txt` removed.
- Done: removed frontend template leftovers (README, notes.txt, .gitignore, App.css, src/assets/, public/icons.svg).
- Skipped by choice: step 3 (CLI files) and step 4 (memory/ out of git).
- Verified: backend imports under `uv run`; `vite build` bundles fine.
- Open: `tsc -b` fails on `App.tsx` because `Chatbox` doesn't accept the `onReply` prop yet (the in-progress reply wiring, not caused by the trim).
