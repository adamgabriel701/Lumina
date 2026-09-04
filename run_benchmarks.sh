#!/bin/bash

echo "========================================="
echo " 🚀 Lumina Language Benchmark Suite "
echo "========================================="

echo "Compilando Lumina (O3 + Native CPU)..."
python3 lumina_cli.py build benchmarks/fib.lm > /dev/null 2>&1
python3 lumina_cli.py build benchmarks/loop.lm > /dev/null 2>&1
python3 lumina_cli.py build benchmarks/primes.lm > /dev/null 2>&1
python3 lumina_cli.py build benchmarks/matrix.lm > /dev/null 2>&1

echo "Compilando C (gcc -O2)..."
gcc -O2 -o benchmarks/fib_c benchmarks/fib.c
gcc -O2 -o benchmarks/loop_c benchmarks/loop.c
gcc -O2 -o benchmarks/primes_c benchmarks/primes.c
gcc -O2 -o benchmarks/matrix_c benchmarks/matrix.c

echo "Compilando C++ (g++ -O2)..."
g++ -O2 -o benchmarks/fib_cpp benchmarks/fib.cpp
g++ -O2 -o benchmarks/loop_cpp benchmarks/loop.cpp
g++ -O2 -o benchmarks/primes_cpp benchmarks/primes.cpp 2>/dev/null
g++ -O2 -o benchmarks/matrix_cpp benchmarks/matrix.cpp

echo "Compilando Rust (rustc -O)..."
rustc -O -o benchmarks/fib_rs benchmarks/fib.rs 2>/dev/null
rustc -O -o benchmarks/loop_rs benchmarks/loop.rs 2>/dev/null
rustc -O -o benchmarks/primes_rs benchmarks/primes.rs 2>/dev/null
rustc -O -o benchmarks/matrix_rs benchmarks/matrix.rs 2>/dev/null

echo "Compilando Go..."
go build -o benchmarks/fib_go benchmarks/fib.go
go build -o benchmarks/loop_go benchmarks/loop.go
go build -o benchmarks/primes_go benchmarks/primes.go
go build -o benchmarks/matrix_go benchmarks/matrix.go

echo ""
echo "-----------------------------------------"
echo "Teste 1: Fibonacci Recursivo (N=35)"
echo "-----------------------------------------"
echo -n "Lumina:   "; start=$(date +%s.%N); ./benchmarks/fib > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"
echo -n "C:        "; start=$(date +%s.%N); ./benchmarks/fib_c > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"
echo -n "Rust:     "; start=$(date +%s.%N); ./benchmarks/fib_rs > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"
echo -n "Go:       "; start=$(date +%s.%N); ./benchmarks/fib_go > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"
echo -n "Node.js:  "; start=$(date +%s.%N); node benchmarks/fib.js > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"
echo -n "Python:   "; start=$(date +%s.%N); python3 benchmarks/fib.py > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"

echo ""
echo "-----------------------------------------"
echo "Teste 2: Loop Matemático (100 Milhões)"
echo "-----------------------------------------"
echo -n "Lumina:   "; start=$(date +%s.%N); ./benchmarks/loop > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"
echo -n "C:        "; start=$(date +%s.%N); ./benchmarks/loop_c > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"
echo -n "Rust:     "; start=$(date +%s.%N); ./benchmarks/loop_rs > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"
echo -n "Go:       "; start=$(date +%s.%N); ./benchmarks/loop_go > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"
echo -n "Node.js:  "; start=$(date +%s.%N); node benchmarks/loop.js > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"

echo ""
echo "-----------------------------------------"
echo "Teste 3: Crivo de Eratóstenes (10 Milhões)"
echo "-----------------------------------------"
echo -n "Lumina:   "; start=$(date +%s.%N); ./benchmarks/primes > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"
echo -n "C:        "; start=$(date +%s.%N); ./benchmarks/primes_c > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"
echo -n "Rust:     "; start=$(date +%s.%N); ./benchmarks/primes_rs > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"
echo -n "Go:       "; start=$(date +%s.%N); ./benchmarks/primes_go > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"

echo ""
echo "-----------------------------------------"
echo "Teste 4: Multiplicação de Matrizes (200x200)"
echo "-----------------------------------------"
echo -n "Lumina:   "; start=$(date +%s.%N); ./benchmarks/matrix > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"
echo -n "C:        "; start=$(date +%s.%N); ./benchmarks/matrix_c > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"
echo -n "Rust:     "; start=$(date +%s.%N); ./benchmarks/matrix_rs > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"
echo -n "Go:       "; start=$(date +%s.%N); ./benchmarks/matrix_go > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"
echo -n "Node.js:  "; start=$(date +%s.%N); node benchmarks/matrix.js > /dev/null; end=$(date +%s.%N); echo " ⏱  $(echo "$end - $start" | bc) s"

echo "========================================="