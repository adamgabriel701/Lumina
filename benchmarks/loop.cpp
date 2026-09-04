#include <iostream>

int main() {
    long long sum = 0;
    long long max = 100000000;
    for (long long i = 0; i < max; i++) {
        sum += i;
    }
    std::cout << "Sum = " << sum << std::endl;
    return 0;
}
