#include <string>
#include <iostream>
int main () {
    std::string user_input;
    
    std::cout << "Enter User Input: ";
    std::getline(std::cin, user_input);
    
    std::cout << user_input << "\n";
}
