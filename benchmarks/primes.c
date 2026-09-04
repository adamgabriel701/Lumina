#include <stdio.h>
#include <stdlib.h>

int main() {
    long long limit = 10000000;
    char *primes = (char*)malloc(limit * sizeof(char));
    
    for (long long i = 0; i < limit; i++) primes[i] = 1;
    primes[0] = 0; primes[1] = 0;
    
    for (long long p = 2; p * p < limit; p++) {
        if (primes[p] == 1) {
            for (long long i = p * p; i < limit; i += p) {
                primes[i] = 0;
            }
        }
    }
    
    long long count = 0;
    for (long long i = 0; i < limit; i++) {
        if (primes[i] == 1) count++;
    }
    
    printf("Primos encontrados: %lld\n", count);
    free(primes);
    return 0;
}
