import os
import httpx
from dotenv import load_dotenv

MODEL = "gemini-3.1-flash-lite"

def call_api(text):
    load_dotenv()
    API_KEY = os.environ["GEMINI_API_KEY"]
    response = httpx.post (
        "https://generativelanguage.googleapis.com/v1beta/interactions",
        headers={"x-goog-api-key": API_KEY},
        json={"model": MODEL, "input": text},
        timeout=30.0,
    )
    
    response.raise_for_status()
    data = response.json()
    reply = next(o["text"] for o in data["outputs"] if o["type"] == "text")
    print (reply)
    return reply
