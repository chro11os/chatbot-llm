
import json
from pathlib import Path

memory_directory = Path.cwd() / "memory/chatmemory.json"
memory_directory.touch(exist_ok=True)

def add_to_history(text):
    data = json.loads(memory_directory.read_text()) if memory_directory.exists() and memory_directory.stat().st_size > 0 else []
    data.append(text)
    memory_directory.write_text(json.dumps(data, indent=4))

    # to do:
        # fix the AttributeError: 'str' object has no attribute 'append'
        # crashed at data.append(text)
        
