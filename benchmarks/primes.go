package main

import "fmt"

func main() {
    limit := 10000000
    primes := make([]byte, limit)
    for i := range primes { primes[i] = 1 }
    primes[0] = 0; primes[1] = 0

    for p := 2; p * p < limit; p++ {
        if primes[p] == 1 {
            for i := p * p; i < limit; i += p {
                primes[i] = 0
            }
        }
    }

    count := 0
    for i := 0; i < limit; i++ {
        if primes[i] == 1 { count++ }
    }
    fmt.Printf("Primos encontrados: %d\n", count)
}
