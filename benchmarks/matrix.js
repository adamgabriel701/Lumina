function main() {
    const n = 200;
    const size = n * n;
    const a = new Int32Array(size);
    const b = new Int32Array(size);
    const c = new Int32Array(size);
    
    for (let i = 0; i < size; i++) {
        a[i] = i % 10;
        b[i] = (i * 2) % 10;
    }
    
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
            let sum = 0;
            for (let k = 0; k < n; k++) {
                sum += a[i * n + k] * b[k * n + j];
            }
            c[i * n + j] = sum;
        }
    }
    console.log(`Matriz C[0][0]: ${c[0]}`);
    console.log(`Matriz C[199][199]: ${c[199 * n + 199]}`);
}
main();
