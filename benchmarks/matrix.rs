fn main() {
    let n = 200;
    let size = n * n;
    let mut a = vec![0i64; size];
    let mut b = vec![0i64; size];
    let mut c = vec![0i64; size];
    
    for i in 0..size {
        a[i] = (i % 10) as i64;
        b[i] = ((i * 2) % 10) as i64;
    }
    
    for i in 0..n {
        for j in 0..n {
            let mut sum = 0;
            for k in 0..n {
                sum += a[i * n + k] * b[k * n + j];
            }
            c[i * n + j] = sum;
        }
    }
    
    println!("Matriz C[0][0]: {}", c[0]);
    println!("Matriz C[199][199]: {}", c[199 * n + 199]);
}
