#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>

const char* LOG_PATH = "chat.log";

void append_message(char role, const std::string& text) {
    std::ofstream out(LOG_PATH, std::ios::binary | std::ios::app);
    uint32_t len = text.size();
    out.write(&role,1);
    out.write(reinterpret_cast<const char*>(&len), sizeof(len));
}