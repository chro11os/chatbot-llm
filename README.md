# chatbot-llm

Chatbot: React frontend -> FastAPI backend -> Gemini, with history stored by a small C++ append-only log engine.

## Run

```
c++ -std=c++17 -O2 -Wall -shared -fPIC -o cse/libcse.dylib cse/engine.cpp -lz   # once, and after editing engine.cpp
uv run fastapi dev server.py                                                     # backend, :8000
cd frontend && bun install && bun run dev                                        # frontend, :5173
```

Needs `GEMINI_API_KEY` in `.env`. CLI instead of the web UI: `uv run main.py`.

## Test the storage engine

```
uv run python cse/test_engine.py
```
