function fib(n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}

const result = fib(35);
console.log(`Fib(35) = ${result}`);
