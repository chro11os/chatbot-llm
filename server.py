import json
from fastapi import FastAPI
from pydantic import BaseModel
from providers.gemini import call_api
from core.json_format import add_to_history, memory_directory

app = FastAPI()

class ChatRequest(BaseModel):
    text: str
@app.post("/api/chat")
def chat(req: ChatRequest):
    reply = call_api(req.text)
    add_to_history({"role": "user", "text": req.text})
    add_to_history({"role": "model", "text": reply})
    return {"reply": reply}

@app.get("/api/history")
def history():
    return json.loads(memory_directory.read_text() or "[]")