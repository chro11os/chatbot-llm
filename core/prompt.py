from providers.gemini import call_api
from core.json_format import add_to_history
from core.json_format import clear_memory

userinput = input("prompt: ")
def prompt():
    if userinput == "/clear":
        clear_memory(userinput)
    else:
        reply = call_api(userinput)
        add_to_history({"role": "user", "text": "userinput"})
        add_to_history({"role": "model", "text": "reply"})
        # fix this later, this only outputs exactly what it has on the chatmemory.json instead of the prompt history
        # anyhow, clear win for today!