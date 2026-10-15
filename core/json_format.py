import json
from pathlib import Path
from core.prompt import userinput

memory_directory = Path.cwd() / "memory/chatmemory.json"
memory_directory.touch(exist_ok=True)

def add_to_history(userinput):
    data = json.loads(memory_directory.read_text()) if memory_directory.exists() and memory_directory.stat().st_size > 0 else []
    data.append(userinput)
    memory_directory.write_text(json.dumps(userinput, indent=4))
