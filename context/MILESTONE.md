# TODOLIST

## Project: Chat Storage Engine (C++)

**Goal:** Replace `memory/chatmemory.json` with a crash-safe, append-only log written in C++.

**Out of scope:** multiple chats, an index, compaction, and frontend changes.

**Definition of done:** the chatbot works exactly as before from the user's side, and history survives a `kill -9` during a write.

## Milestone 1: Design

- [ ] **CSE-1: Write the format spec** (Priority: high)
  - Define every record field, its size and its byte order.
  - Decide how the file identifies itself and its format version.
  - Done when: you can decode a record by hand from a hex dump.
- [ ] **CSE-2: Decide how a turn is saved** (Priority: high)
  - Choose one record per turn or two records, and write down why.
  - Done when: you've written down what happens if a crash lands between the user message and the reply.

## Milestone 2: Core log

- [ ] **CSE-3: Append a record** (Depends on: CSE-1)
  - Done when: `cse/main.cpp` appends 3 messages, and `hexdump` shows bytes matching your spec.
- [ ] **CSE-4: Read all records** (Depends on: CSE-3)
  - Done when: messages come back identical and in order, including empty text, newlines, quotes and non-English text.
- [ ] **CSE-5: Run clean under the memory tools** (Depends on: CSE-4)
  - Done when: `valgrind` and AddressSanitizer report no errors or leaks.

## Milestone 3: Crash safety

- [ ] **CSE-6: Add checksums** (Depends on: CSE-4)
  - Done when: changing any single byte in a record is detected on read.
- [ ] **CSE-7: Flush before reporting success** (Depends on: CSE-3)
  - Done when: the engine only returns success after the flush succeeds, and a failed write returns an error.
- [ ] **CSE-8: Recover on open** (Depends on: CSE-6, CSE-7)
  - Done when: after you cut the file at 10 different points, every complete record survives and new appends still work.
- [ ] **CSE-9: Handle middle-of-file damage** (Depends on: CSE-8)
  - Decide how this differs from a torn final record.
  - Done when: the engine never deletes valid data silently, and the behavior is written down.
- [ ] **CSE-10: Kill test** (Depends on: CSE-8)
  - Done when: a script runs `kill -9` during writes 100 times, and no acknowledged message is lost.

## Milestone 4: Clear and concurrency

- [ ] **CSE-11: Clear** (Depends on: CSE-4)
  - Done when: reads return nothing after a clear, later appends appear normally, and this survives a restart.
- [ ] **CSE-12: Thread safety** (Depends on: CSE-4)
  - Done when: 8 threads appending 1,000 messages each produce exactly 8,000 valid records.
- [ ] **CSE-13: Single-process lock** (Depends on: CSE-8)
  - Done when: a second process gets a clear error, and the lock is available again after the first one is killed.

## Milestone 5: Integration

- [ ] **CSE-14: Build the shared library** (Depends on: Milestone 4)
  - Done when: a small standalone Python script can append and read through `ctypes`.
- [ ] **CSE-15: Migrate existing history** (Depends on: CSE-14)
  - Done when: all 24 messages are in the log, and `chatmemory.json` is kept as a backup.
- [ ] **CSE-16: Swap the storage layer** (Depends on: CSE-14)
  - Update `core/json_format.py` and the `/api/history` read in `server.py`.
  - Done when: `/api/chat`, `/api/history` and the CLI's `/clear` all behave as they did before.
- [ ] **CSE-17: Final acceptance** (Depends on: all tickets)
  - Done when: you can kill the server mid-chat, restart it, and `/api/history` returns the full, valid history.
