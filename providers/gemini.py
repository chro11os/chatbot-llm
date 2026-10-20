import json
from pathlib import Path
import os
import httpx
from dotenv import load_dotenv

MODEL = "gemini-3.5-flash-lite"

def call_api(text):
    load_dotenv()
    API_KEY = os.environ["GEMINI_API_KEY"]
    response = httpx.post (
        "https://generativelanguage.googleapis.com/v1beta/interactions",
        headers={"x-goog-api-key": API_KEY},
        json={"model": MODEL, "input": text},
        timeout=30.0,
    )
    if response.is_error:
        print(response.text)
    response.raise_for_status()
    data = response.json()
    Path("memory/lastresponse.json").write_text(json.dumps(data, indent=4))

    reply = ""
    for step in data["steps"]:
        if step["type"] == "model_output":
            for part in step["content"]:
                if part["type"] == "text":
                    reply += part["text"]
    print (reply)
    return reply

    # i might be losing my mind