fn main() {
    let limit: usize = 10000000;
    let mut primes = vec![1u8; limit];
    primes[0] = 0; primes[1] = 0;
    
    let mut p = 2;
    while p * p < limit {
        if primes[p] == 1 {
            let mut i = p * p;
            while i < limit {
                primes[i] = 0;
                i += p;
            }
        }
        p += 1;
    }
    
    let count = primes.iter().filter(|&x| *x == 1).count();
    println!("Primos encontrados: {}", count);
}
