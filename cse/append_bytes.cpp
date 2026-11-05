#include <fstream>
#include <string>

int main () {
    std::ofstream file("widgets.log", std::ios::binary | std::ios::app);
    std::string name = "gear";
    file.write(name.data(), name.size());
}