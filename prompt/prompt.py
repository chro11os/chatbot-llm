from pathlib import Path
from gemini_api.api import call_api
import json

def prompt():
    memory_directory = Path.cwd() / "chatmemory.json"
    memory_directory.touch(exist_ok=True)

    userinput = input("prompt: ")
    formatted_prompt = json.dumps(userinput)

    with memory_directory.open("a") as file:
        file.write(formatted_prompt)
        call_api(formatted_prompt)
