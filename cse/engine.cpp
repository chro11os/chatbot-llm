// Chat storage engine: an append-only, crash-safe log of opaque byte records.
//
// File layout:  "CSE1" | record | record | ...
// Record:       [u32 len][u32 crc32(payload)][payload: len bytes]
//
// Python (core/json_format.py) decides what a payload means (one JSON turn).
// Build: see README.md.
#include <algorithm>
#include <cerrno>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <vector>

#include <fcntl.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <unistd.h>
#include <zlib.h>

namespace {

const char MAGIC[4] = {'C', 'S', 'E', '1'};
constexpr size_t HEADER = sizeof(MAGIC);
constexpr size_t REC_HDR = 8;  // len + crc
// ponytail: lengths/crcs are stored in native byte order (little-endian on every Mac); fix the order if the file ever moves between architectures

struct Engine {
    int fd = -1;
    std::mutex mu;  // threads in this process (FastAPI runs `def` routes on a thread pool)
    ~Engine() { if (fd >= 0) close(fd); }
};

// flock = other processes (CLI + server). Same-fd threads don't block each other on flock, hence the mutex too.
struct FileLock {
    int fd;
    FileLock(int fd, int op) : fd(fd) { if (flock(fd, op) != 0) throw std::runtime_error("flock"); }
    ~FileLock() { flock(fd, LOCK_UN); }
};

bool sync_to_disk(int fd) {
#ifdef F_FULLFSYNC
    if (fcntl(fd, F_FULLFSYNC) == 0) return true;  // macOS: plain fsync doesn't flush the drive's cache
#endif
    return fsync(fd) == 0;
}

void write_all(int fd, const uint8_t* p, size_t n) {
    while (n > 0) {
        ssize_t w = write(fd, p, n);
        if (w < 0) {
            if (errno == EINTR) continue;
            throw std::runtime_error("write");
        }
        p += w;
        n -= w;
    }
}

std::vector<uint8_t> read_file(int fd) {
    struct stat st;
    if (fstat(fd, &st) != 0) throw std::runtime_error("fstat");
    std::vector<uint8_t> b(st.st_size);
    size_t got = 0;
    while (got < b.size()) {
        ssize_t r = pread(fd, b.data() + got, b.size() - got, got);
        if (r < 0 && errno == EINTR) continue;
        if (r <= 0) throw std::runtime_error("pread");
        got += r;
    }
    return b;
}

uint32_t checksum(const uint8_t* p, uint32_t n) {
    return static_cast<uint32_t>(crc32(0, p, n));
}

enum class Scan { Ok, Torn, Corrupt };

// Walks the records; `good` ends at the last record that checks out.
// Torn   = the damage is the final record (a write that never finished) -> safe to cut off.
// Corrupt = a bad record with more data after it -> don't guess, refuse.
// ponytail: a damaged *length* field mid-file can look torn and get cut; a resync marker per record would catch that
Scan scan(const std::vector<uint8_t>& b, size_t& good) {
    good = HEADER;
    while (good < b.size()) {
        size_t left = b.size() - good;
        if (left < REC_HDR) return Scan::Torn;
        uint32_t len, crc;
        std::memcpy(&len, &b[good], 4);
        std::memcpy(&crc, &b[good + 4], 4);
        if (left - REC_HDR < len) return Scan::Torn;
        if (checksum(&b[good + REC_HDR], len) != crc)
            return good + REC_HDR + len == b.size() ? Scan::Torn : Scan::Corrupt;
        good += REC_HDR + len;
    }
    return Scan::Ok;
}

}  // namespace

// C API: no logic, no exceptions across the boundary. 0 = ok, -1 = error.
extern "C" {

void* cse_open(const char* path) noexcept {
    try {
        auto e = std::make_unique<Engine>();
        e->fd = open(path, O_RDWR | O_CREAT | O_APPEND | O_CLOEXEC, 0644);
        if (e->fd < 0) return nullptr;
        FileLock lock(e->fd, LOCK_EX);

        auto b = read_file(e->fd);
        if (b.size() < HEADER && std::equal(b.begin(), b.end(), MAGIC)) {
            // new file, or a crash while writing the header
            if (ftruncate(e->fd, 0) != 0) return nullptr;
            write_all(e->fd, reinterpret_cast<const uint8_t*>(MAGIC), HEADER);
            if (!sync_to_disk(e->fd)) return nullptr;
        } else if (b.size() < HEADER || std::memcmp(b.data(), MAGIC, HEADER) != 0) {
            return nullptr;  // not our file
        } else {
            size_t good;
            switch (scan(b, good)) {
                case Scan::Ok: break;
                case Scan::Torn:
                    if (ftruncate(e->fd, good) != 0 || !sync_to_disk(e->fd)) return nullptr;
                    break;
                case Scan::Corrupt: return nullptr;
            }
        }
        return e.release();
    } catch (...) {
        return nullptr;
    }
}

int cse_append(void* h, const uint8_t* data, uint32_t len) noexcept {
    try {
        auto* e = static_cast<Engine*>(h);
        // Encode first so the whole record goes out in one write()
        std::vector<uint8_t> rec(REC_HDR + len);
        uint32_t crc = checksum(data, len);
        std::memcpy(&rec[0], &len, 4);
        std::memcpy(&rec[4], &crc, 4);
        if (len) std::memcpy(&rec[REC_HDR], data, len);

        std::lock_guard<std::mutex> guard(e->mu);
        FileLock lock(e->fd, LOCK_EX);
        off_t start = lseek(e->fd, 0, SEEK_END);
        try {
            write_all(e->fd, rec.data(), rec.size());
            if (!sync_to_disk(e->fd)) throw std::runtime_error("sync");
        } catch (...) {
            // Don't leave half a record in front of the next append
            if (ftruncate(e->fd, start) == 0) sync_to_disk(e->fd);
            return -1;
        }
        return 0;  // success only after the data is on disk
    } catch (...) {
        return -1;
    }
}

// Returns every record (framing included, header stripped) in one malloc'd buffer; free it with cse_free.
int cse_read_all(void* h, uint8_t** out, uint64_t* out_len) noexcept {
    try {
        auto* e = static_cast<Engine*>(h);
        std::vector<uint8_t> b;
        {
            std::lock_guard<std::mutex> guard(e->mu);
            FileLock lock(e->fd, LOCK_SH);
            b = read_file(e->fd);
        }
        size_t good;
        if (b.size() < HEADER || scan(b, good) != Scan::Ok) return -1;
        size_t n = b.size() - HEADER;
        auto* p = static_cast<uint8_t*>(std::malloc(n ? n : 1));
        if (!p) return -1;
        if (n) std::memcpy(p, b.data() + HEADER, n);
        *out = p;
        *out_len = n;
        return 0;
    } catch (...) {
        return -1;
    }
}

void cse_free(uint8_t* p) noexcept { std::free(p); }

int cse_clear(void* h) noexcept {
    try {
        auto* e = static_cast<Engine*>(h);
        std::lock_guard<std::mutex> guard(e->mu);
        FileLock lock(e->fd, LOCK_EX);
        return ftruncate(e->fd, HEADER) == 0 && sync_to_disk(e->fd) ? 0 : -1;
    } catch (...) {
        return -1;
    }
}

void cse_close(void* h) noexcept { delete static_cast<Engine*>(h); }

}  // extern "C"
