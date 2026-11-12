from providers.gemini import call_api
from core.json_format import add_turn, clear_memory

def prompt():
    while True:
        userinput = input("prompt: ")
        match userinput:
            case "/clear":
                clear_memory(userinput)
                continue
            case "/quit" | "/end":
                break

        reply, _ = call_api(userinput)
        add_turn(userinput, reply)
