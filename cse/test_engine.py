# Run from the project root after building cse/libcse.dylib:
#   uv run python cse/test_engine.py
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from core.json_format import Log  # noqa: E402

tmp = Path(tempfile.mkdtemp())
p = tmp / "t.log"

# 1. Round trip (newlines + non-ASCII) and 8 threads appending at once
log = Log(p)
log.append([{"role": "user", "text": "hi\nthere ✨"}])
def spam():
    for _ in range(50):
        log.append([{"role": "model", "text": "x" * 1000}])
threads = [threading.Thread(target=spam) for _ in range(8)]
for t in threads: t.start()
for t in threads: t.join()
msgs = log.read()
assert len(msgs) == 401 and msgs[0]["text"] == "hi\nthere ✨"
log.close()

# 2. Torn final record (crash mid-write): open cuts it off, earlier records survive
good_size = p.stat().st_size
with open(p, "ab") as f:
    f.write(b"\x10\x00\x00\x00garb")
log = Log(p)
assert len(log.read()) == 401 and p.stat().st_size == good_size
log.close()

# 3. Damage in the middle: open refuses instead of guessing
b = bytearray(p.read_bytes())
b[4 + 8 + 2] ^= 0xFF  # a payload byte of the first record
p.write_bytes(b)
try:
    Log(p)
    raise AssertionError("opened a log with mid-file damage")
except OSError:
    pass

# 4. Clear
p.unlink()
log = Log(p)
log.append([{"role": "user", "text": "a"}])
log.clear()
assert log.read() == []
log.close()

# 5. kill -9 while another process is appending: the log still opens and reads
p.unlink()
code = (f"import sys; sys.path.insert(0, {str(ROOT)!r}); from core.json_format import Log\n"
        f"l = Log({str(p)!r})\nwhile True: l.append([{{'role': 'user', 'text': 'y' * 5000}}])")
proc = subprocess.Popen([sys.executable, "-c", code])
time.sleep(1.5)
proc.send_signal(signal.SIGKILL)
proc.wait()
n = len(Log(p).read())
assert n > 0

print(f"ok ({n} records survived kill -9)")
