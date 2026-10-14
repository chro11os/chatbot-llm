from providers.gemini import call_api
import json
from pathlib import Path

userinput = input("prompt: ")
history_list = [userinput]


def prompt():
    # create the file and the path ignore if exist
    memory_directory = Path.cwd() / "memory/chatmemory.json"
    memory_directory.touch(exist_ok=True)

    # dumps the user input in the json file
    formatted_prompt = json.dumps(history_list, indent=4)

    # add another us inputted item to the list
    history_list.append(userinput)

    # -> maybe this is where the logic breaks since if the code before this adds user input
    # then wth is the use of this?? or maybe this is the only one that should exist??
    with memory_directory.open("a+") as file:
        file.write(formatted_prompt + "\n")
    print(formatted_prompt)
    # call_api(formatted_prompt)


def format_memory_json():
    path = Path("memory/chatmemory.json")
