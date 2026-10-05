from pathlib import Path
from providers.gemini import call_api
import json

def prompt():
    memory_directory = Path.cwd() / "memory/chatmemory.json"
    memory_directory.touch(exist_ok=True)

    userinput = input("prompt: ")
    formatted_prompt = json.dumps(userinput)

    with memory_directory.open("a") as file:
        file.write(formatted_prompt + "\n")
    print(formatted_prompt)
    # call_api(formatted_prompt)

def format_memory_json():
    path = Path("memory/chatmemory.json")


    
