#include <iostream>

long long fib(long long n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}

int main() {
    long long result = fib(35);
    std::cout << "Fib(35) = " << result << std::endl;
    return 0;
}
