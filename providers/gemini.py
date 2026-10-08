import os
import httpx
from dotenv import load_dotenv

def call_api(text):
    load_dotenv()
    API_KEY = os.environ["GEMINI_API_KEY"]
    response = httpx.post(
        "https://generativelanguage.googleapis.com/v1beta/interactions",
        headers={"x-goog-api-key": API_KEY},
        json={"model": "gemini-3.1-flash-lite", "input": text},
        timeout=30.0,
    )
