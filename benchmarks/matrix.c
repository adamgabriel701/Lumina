#include <stdio.h>
#include <stdlib.h>

int main() {
    int n = 200;
    int size = n * n;
    int *a = (int*)malloc(size * sizeof(int));
    int *b = (int*)malloc(size * sizeof(int));
    int *c = (int*)malloc(size * sizeof(int));
    
    for (int i = 0; i < size; i++) {
        a[i] = i % 10;
        b[i] = (i * 2) % 10;
    }
    
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            int sum = 0;
            for (int k = 0; k < n; k++) {
                sum += a[i * n + k] * b[k * n + j];
            }
            c[i * n + j] = sum;
        }
    }
    
    printf("Matriz C[0][0]: %d\n", c[0]);
    printf("Matriz C[199][199]: %d\n", c[199 * n + 199]);
    free(a); free(b); free(c);
    return 0;
}
