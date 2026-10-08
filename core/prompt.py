import json
from pathlib import Path

from providers.gemini import call_api

userinput = input("prompt: ")
history_list = [userinput]


def prompt():
    memory_directory = Path.cwd() / "memory/chatmemory.json"
    memory_directory.touch(exist_ok=True)

    formatted_prompt = json.dumps(history_list, indent=4)
    json.load(formatted_prompt)
    
    history_list.append(userinput)

    with memory_directory.open("a+") as file:
        file.write(formatted_prompt + "\n")
    print(formatted_prompt)
    # call_api(formatted_prompt)


def format_memory_json():
    path = Path("memory/chatmemory.json")
