package main

import "fmt"

func main() {
    n := 200
    size := n * n
    a := make([]int64, size)
    b := make([]int64, size)
    c := make([]int64, size)
    
    for i := 0; i < size; i++ {
        a[i] = int64(i % 10)
        b[i] = int64((i * 2) % 10)
    }
    
    for i := 0; i < n; i++ {
        for j := 0; j < n; j++ {
            var sum int64 = 0
            for k := 0; k < n; k++ {
                sum += a[i * n + k] * b[k * n + j]
            }
            c[i * n + j] = sum
        }
    }
    fmt.Printf("Matriz C[0][0]: %d\n", c[0])
    fmt.Printf("Matriz C[199][199]: %d\n", c[199 * n + 199])
}
