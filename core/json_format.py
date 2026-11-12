"""Chat history, stored by the C++ engine (cse/engine.cpp) through ctypes.

Each record is one JSON list of messages: a whole turn [user, model] is one
record, so a crash can't save a question without its answer.
"""
import ctypes
import json
import struct
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = ROOT / "memory" / "chat.log"
OLD_JSON = ROOT / "memory" / "chatmemory.json"

_lib = ctypes.CDLL(str(ROOT / "cse" / "libcse.dylib"))  # build it first, see README.md
_bytes_p = ctypes.POINTER(ctypes.c_uint8)
_lib.cse_open.restype = ctypes.c_void_p  # opaque handle; default int return would cut a 64-bit pointer
_lib.cse_open.argtypes = [ctypes.c_char_p]
_lib.cse_append.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32]
_lib.cse_read_all.argtypes = [ctypes.c_void_p, ctypes.POINTER(_bytes_p), ctypes.POINTER(ctypes.c_uint64)]
_lib.cse_free.argtypes = [_bytes_p]
_lib.cse_clear.argtypes = [ctypes.c_void_p]
_lib.cse_close.argtypes = [ctypes.c_void_p]


class Log:
    def __init__(self, path):
        self._h = _lib.cse_open(str(path).encode())
        if not self._h:
            raise OSError(f"cse_open failed for {path} (unreadable, not a CSE file, or damaged mid-file)")

    def append(self, messages):
        data = json.dumps(messages).encode()
        if _lib.cse_append(self._h, data, len(data)) != 0:
            raise OSError("cse_append failed")

    def read(self):
        buf, n = _bytes_p(), ctypes.c_uint64()
        if _lib.cse_read_all(self._h, ctypes.byref(buf), ctypes.byref(n)) != 0:
            raise OSError("cse_read_all failed")
        try:
            data = ctypes.string_at(buf, n.value)
        finally:
            _lib.cse_free(buf)  # C++ allocated it, C++ frees it
        messages, i = [], 0
        while i < len(data):
            length, _crc = struct.unpack_from("<II", data, i)
            messages.extend(json.loads(data[i + 8:i + 8 + length]))
            i += 8 + length
        return messages

    def clear(self):
        if _lib.cse_clear(self._h) != 0:
            raise OSError("cse_clear failed")

    def close(self):
        _lib.cse_close(self._h)
        self._h = None


@cache
def _log():
    LOG_PATH.parent.mkdir(exist_ok=True)
    log = Log(LOG_PATH)
    # One-time move of the old JSON history into the log
    if OLD_JSON.exists() and not log.read():
        for message in json.loads(OLD_JSON.read_text() or "[]"):
            log.append([message])
        OLD_JSON.rename(OLD_JSON.with_name("chatmemory.json.imported"))
    return log


def add_turn(user_text, model_text, session="cli"):
    _log().append([
        {"role": "user", "text": user_text, "session": session},
        {"role": "model", "text": model_text, "session": session},
    ])


def read_history():
    return _log().read()


def clear_memory(userinput):
    if userinput == "/clear":
        _log().clear()
        print("chat history cleared")
