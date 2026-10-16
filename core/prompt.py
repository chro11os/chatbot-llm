from providers.gemini import call_api
from core.json_format import add_to_history

userinput = input("prompt: ")
def prompt():
    # call_api(userinput)
    add_to_history(userinput)
    