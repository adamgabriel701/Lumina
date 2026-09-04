package main

import "fmt"

func main() {
    var sum int = 0
    var max int = 100000000
    for i := 0; i < max; i++ {
        sum += i
    }
    fmt.Printf("Sum = %d\n", sum)
}
