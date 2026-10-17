
import json
from pathlib import Path

memory_directory = Path.cwd() / "memory/chatmemory.json"
memory_directory.touch(exist_ok=True)

def add_to_history(text):
    data = json.loads(memory_directory.read_text()) if memory_directory.exists() and memory_directory.stat().st_size > 0 else []
    data.append(text)
    memory_directory.write_text(json.dumps(data, indent=4))

def clear_memory(userinput):
    if userinput == "/clear":
        memory_directory.write_text("[]")
        print ("chat history cleared")
    else:
        return
        
