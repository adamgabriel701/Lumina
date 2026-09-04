#include <stdio.h>
#include <stdlib.h>

long long fib(long long n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}

int main() {
    long long result = fib(35);
    printf("Fib(35) = %lld\n", result);
    return 0;
}
