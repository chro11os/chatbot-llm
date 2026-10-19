from providers.gemini import call_api
from core.json_format import add_to_history
from core.json_format import clear_memory

def prompt():
    end:bool = False
    while end == False:
        userinput = input("prompt: ")
        match userinput:
            case "/clear":
                clear_memory(userinput)    
            case "/quit" | "/end":
                end = True
        reply = call_api(userinput)
        add_to_history({"role": "user", "text": userinput})
        add_to_history({"role": "model", "text": reply})