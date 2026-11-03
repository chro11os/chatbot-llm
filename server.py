import json
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from providers.gemini import call_api
from core.json_format import add_to_history, memory_directory

app = FastAPI()

class ChatRequest(BaseModel):
    text: str
@app.post("/api/chat")
def chat(req: ChatRequest):
    
    try:
        reply = call_api(req.text)
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Gemini took too long to respond.")
    
    add_to_history({"role": "user", "text": req.text})
    add_to_history({"role": "model", "text": reply})
    
    return {"reply": reply}

@app.get("/api/history")
def history():
    return json.loads(memory_directory.read_text() or "[]")