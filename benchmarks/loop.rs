fn main() {
    let mut sum: i64 = 0;
    let max: i64 = 100000000;
    for i in 0..max {
        sum += i;
    }
    println!("Sum = {}", sum);
}
