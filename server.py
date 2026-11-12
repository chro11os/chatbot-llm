import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from providers.gemini import call_api
from core.json_format import add_turn, read_history

app = FastAPI()

class ChatRequest(BaseModel):
    text: str
    session: str

@app.post("/api/chat")
def chat(req: ChatRequest):
    try:
        reply, usage = call_api(req.text)
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Gemini took too long to respond.")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Gemini returned {e.response.status_code}: {e.response.text[:300]}")

    add_turn(req.text, reply, req.session)  # one record per turn: both messages or neither
    return {"reply": reply, "usage": usage}

@app.get("/api/history")
def history():
    return read_history()
