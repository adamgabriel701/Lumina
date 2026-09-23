/* linker/runtime/rt.c — runtime freestanding do Lumina
 *
 * Compilar:
 *   clang -c -ffreestanding -fno-pic -fno-pie \
 *         -fno-stack-protector -fno-builtin -nostdlib \
 *         -O2 rt.c -o rt.o
 *
 * Fornece: malloc/free/calloc, mem*, strings, printf/snprintf/putchar,
 *          FILE* mínimo, I/O por fd (open/read/write/lseek),
 *          math (pow/sqrt/abs/labs/floor/ceil/round/rand), usleep, remove, sockets/epoll
 *          e shims do Boehm GC.
 */
typedef unsigned long size_t;
typedef long          ssize_t;

/* ================= forward declarations =================
 * Necessárias porque funções como `calloc` chamam `memset`,
 * `fopen` chama `malloc`, e `pow` chama `sqrt`-like helpers,
 * antes das definições aparecerem. */
void  *malloc(size_t);
void   free(void*);
void  *calloc(size_t, size_t);
void  *memset(void*, int, size_t);
void  *memcpy(void*, const void*, size_t);
void  *memmove(void*, const void*, size_t);
int    memcmp(const void*, const void*, size_t);
size_t strlen(const char*);
int    strcmp(const char*, const char*);
int    strncmp(const char*, const char*, size_t);
char  *strcpy(char*, const char*);
char  *strncpy(char*, const char*, size_t);
char  *strcat(char*, const char*);
int puts(const char*);
char  *strstr(const char*, const char*);
long   atoi(const char*);
int    putchar(int);
int    getchar(void);
int    usleep(unsigned int);
int    remove(const char*);
int    printf(const char*, ...);
int    snprintf(char*, size_t, const char*, ...);
void   abort(void);
void  *fopen(const char*, const char*);
int    fclose(void*);
size_t fread(void*, size_t, size_t, void*);
size_t fwrite(const void*, size_t, size_t, void*);
int    fseek(void*, long, int);
long   ftell(void*);
char  *fgets(char*, int, void*);
int    fputs(const char*, void*);
int    fflush(void*);
double pow(double, double);
double sqrt(double);
double floor(double);
double ceil(double);
double round(double);
int    abs(int);
long   labs(long);
int    rand(void);
void   srand(unsigned int);
int    open(const char*, int, ...);
int    close(int);
long   read(int, void*, size_t);
long   write(int, const void*, size_t);
long   lseek(int, long, int);
void   GC_init(void);
void  *GC_malloc(size_t);
void   GC_free(void*);

/* ================= syscalls Linux x86_64 ================= */

static long _sys1(long n, long a) {
    long r;
    __asm__ volatile("syscall"
        : "=a"(r) : "a"(n), "D"(a) : "rcx", "r11", "memory");
    return r;
}
static long _sys2(long n, long a, long b) {
    long r;
    __asm__ volatile("syscall"
        : "=a"(r) : "a"(n), "D"(a), "S"(b) : "rcx", "r11", "memory");
    return r;
}
static long _sys3(long n, long a, long b, long c) {
    long r;
    __asm__ volatile("syscall"
        : "=a"(r) : "a"(n), "D"(a), "S"(b), "d"(c)
        : "rcx", "r11", "memory");
    return r;
}
static long _sys4(long n, long a, long b, long c, long d) {
    long r;
    register long r10 __asm__("r10") = d;
    __asm__ volatile("syscall"
        : "=a"(r) : "a"(n), "D"(a), "S"(b), "d"(c), "r"(r10)
        : "rcx", "r11", "memory");
    return r;
}
static long _sys5(long n, long a, long b, long c, long d, long e) {
    long r;
    register long r10 __asm__("r10") = d;
    register long r8  __asm__("r8")  = e;
    __asm__ volatile("syscall"
        : "=a"(r) : "a"(n), "D"(a), "S"(b), "d"(c), "r"(r10), "r"(r8)
        : "rcx", "r11", "memory");
    return r;
}

static void _write_fd(int fd, const void *buf, size_t n) {
    _sys3(1, fd, (long)buf, (long)n);
}
static void _exit(int code) {
    _sys1(60, code);
    __builtin_unreachable();
}

/* ================= memória (brk) ================= */

extern char _end;
static char *_heap = 0;

void *malloc(size_t n) {
    if (!_heap) _heap = (char*)(((unsigned long)&_end + 4095) & ~4095UL);
    char *p = _heap;
    _heap += (n + 15) & ~15UL;
    _sys1(12, (long)_heap);
    return p;
}
void free(void *p) { (void)p; }

void *calloc(size_t n, size_t sz) {
    size_t total = n * sz;
    void *p = malloc(total);
    if (p) memset(p, 0, total);
    return p;
}

/* ================= mem* ================= */

void *memset(void *d, int c, size_t n) {
    unsigned char *p = (unsigned char*)d;
    while (n--) *p++ = (unsigned char)c;
    return d;
}
void *memcpy(void *d, const void *s, size_t n) {
    unsigned char *dp = (unsigned char*)d;
    const unsigned char *sp = (const unsigned char*)s;
    while (n--) *dp++ = *sp++;
    return d;
}
void *memmove(void *d, const void *s, size_t n) {
    unsigned char *dp = (unsigned char*)d;
    const unsigned char *sp = (const unsigned char*)s;
    if (dp < sp) {
        while (n--) *dp++ = *sp++;
    } else {
        dp += n; sp += n;
        while (n--) *--dp = *--sp;
    }
    return d;
}
int memcmp(const void *a, const void *b, size_t n) {
    const unsigned char *pa = a, *pb = b;
    while (n--) {
        if (*pa != *pb) return (int)*pa - (int)*pb;
        pa++; pb++;
    }
    return 0;
}

/* ================= strings ================= */

size_t strlen(const char *s) {
    size_t n = 0;
    while (s[n]) n++;
    return n;
}

int strcmp(const char *a, const char *b) {
    while (*a && *a == *b) { a++; b++; }
    return (unsigned char)*a - (unsigned char)*b;
}

int strncmp(const char *a, const char *b, size_t n) {
    while (n && *a && *a == *b) { a++; b++; n--; }
    return n ? ((unsigned char)*a - (unsigned char)*b) : 0;
}

char *strcpy(char *d, const char *s) {
    char *o = d;
    do { *d++ = *s; } while (*s++);
    return o;
}

char *strncpy(char *d, const char *s, size_t n) {
    char *o = d;
    while (n && (*d = *s)) { d++; s++; n--; }
    while (n--) *d++ = 0;
    return o;
}

char *strcat(char *d, const char *s) {
    char *o = d;
    while (*d) d++;
    do { *d++ = *s; } while (*s++);
    return o;
}

int puts(const char *s) {
    size_t n = strlen(s);
    _write_fd(1, s, n);
    _write_fd(1, "\n", 1);
    return (int)(n + 1);
}

char *strstr(const char *h, const char *n) {
    if (!*n) return (char*)h;
    for (; *h; h++) {
        const char *a = h, *b = n;
        while (*a && *b && *a == *b) { a++; b++; }
        if (!*b) return (char*)h;
    }
    return 0;
}

long atoi(const char *s) {
    long v = 0;
    int neg = 0;
    while (*s == ' ' || *s == '\t') s++;
    if (*s == '-') { neg = 1; s++; }
    else if (*s == '+') s++;
    while (*s >= '0' && *s <= '9') v = v * 10 + (*s++ - '0');
    return neg ? -v : v;
}

/* ================= putchar / getchar ================= */

int putchar(int c) {
    unsigned char ch = (unsigned char)c;
    _write_fd(1, &ch, 1);
    return c;
}

int getchar(void) {
    char c;
    long r = _sys3(0, 0, (long)&c, 1);
    return r > 0 ? (unsigned char)c : -1;
}

/* ================= usleep ================= */

int usleep(unsigned int usec) {
    struct { long tv_sec; long tv_nsec; } ts;
    ts.tv_sec  = usec / 1000000UL;
    ts.tv_nsec = (long)(usec % 1000000UL) * 1000L;
    return (int)_sys2(35, (long)&ts, 0);   /* nanosleep */
}

/* ================= remove (unlink) ================= */

int remove(const char *path) {
    long r = _sys1(87, (long)path);        /* unlink */
    return r < 0 ? -1 : 0;
}

/* ================= math ================= */

int abs(int x) { return x < 0 ? -x : x; }
long labs(long x) { return x < 0 ? -x : x; }

double floor(double x) {
    long i = (long)x;
    return (x < 0.0 && x != (double)i) ? (double)(i - 1) : (double)i;
}

double ceil(double x) {
    long i = (long)x;
    return (x > 0.0 && x != (double)i) ? (double)(i + 1) : (double)i;
}

double round(double x) {
    return (x >= 0.0) ? (double)(long)(x + 0.5) : (double)(long)(x - 0.5);
}

double sqrt(double x) {
    if (x <= 0.0) return 0.0;
    /* Newton-Raphson partindo do próprio x. Converge em ~5-6
       iterações para qualquer x razoável. */
    double r = x;
    for (int i = 0; i < 30; i++) r = 0.5 * (r + x / r);
    return r;
}

double pow(double base, double exp) {
    /* Casos rápidos: exp inteiro pequeno. Para exp não-inteiro,
       cobre exp == 0.5 via sqrt e cai num fallback com ln+série. */
    if (exp == 0.0) return 1.0;
    if (exp == 1.0) return base;
    if (exp == 2.0) return base * base;
    if (exp == 0.5) return sqrt(base);

    int neg = 0;
    if (exp < 0.0) { neg = 1; exp = -exp; }

    long ie = (long)exp;
    if ((double)ie == exp) {
        double r = 1.0, b = base;
        while (ie > 0) {
            if (ie & 1) r *= b;
            b *= b;
            ie >>= 1;
        }
        return neg ? 1.0 / r : r;
    }

    /* Fallback: exp*ln(base) via série. Só cobre base > 0. */
    if (base <= 0.0) return 0.0;
    double m = base, k = 0.0;
    while (m > 2.0) { m *= 0.5; k += 1.0; }
    while (m < 0.5) { m *= 2.0; k -= 1.0; }
    double z = (m - 1.0) / (m + 1.0);
    double z2 = z * z, term = z, ln = 0.0;
    for (int i = 0; i < 30; i++) {
        ln += term / (2.0 * i + 1.0);
        term *= z2;
    }
    ln *= 2.0;
    ln += k * 0.69314718055994530942;

    double r = 1.0, b = base;
    long n = (long)exp;
    while (n > 0) {
        if (n & 1) r *= b;
        b *= b;
        n >>= 1;
    }
    double frac = exp - (double)(long)exp;
    r *= 1.0 + frac * ln;
    return neg ? 1.0 / r : r;
}

/* ================= rand / srand ================= */
/* LCG (Linear Congruential Generator) simples. */
static unsigned long _rand_seed = 1;

void srand(unsigned int seed) {
    _rand_seed = seed;
}

int rand(void) {
    _rand_seed = (_rand_seed * 1103515245UL + 12345UL) & 0x7fffffffUL;
    return (int)_rand_seed;
}

/* ================= I/O por fd ================= */

int open(const char *path, int flags, ...) {
    /* flags usam os mesmos valores Linux: O_RDONLY=0, O_WRONLY=1,
       O_RDWR=2, O_CREAT=0x40, O_TRUNC=0x200, O_APPEND=0x400 */
    long r = _sys3(2, (long)path, flags, 0644);
    return (int)r;
}

int close(int fd) {
    long r = _sys1(3, fd);
    return (int)r;
}

long read(int fd, void *buf, size_t n) {
    return _sys3(0, fd, (long)buf, (long)n);
}

long write(int fd, const void *buf, size_t n) {
    return _sys3(1, fd, (long)buf, (long)n);
}

long lseek(int fd, long off, int whence) {
    return _sys3(8, fd, off, whence);
}

/* ================= printf / snprintf ================= */

static int _format_to(char *dst, size_t cap, const char *fmt, __builtin_va_list ap) {
    size_t i = 0;
    #define PUT(c) do { if (i < cap - 1) dst[i] = (c); i++; } while (0)

    for (const char *p = fmt; *p; p++) {
        if (*p != '%') { PUT(*p); continue; }
        p++;
        switch (*p) {
        case 's': {
            const char *s = __builtin_va_arg(ap, const char*);
            if (!s) s = "(null)";
            while (*s) PUT(*s++);
            break;
        }
        case 'c': {
            int c = __builtin_va_arg(ap, int);
            PUT((char)c);
            break;
        }
        case 'd': {
            int v = __builtin_va_arg(ap, int);
            char tmp[16]; int k = 0;
            unsigned int u = (v < 0) ? (unsigned)(-v) : (unsigned)v;
            if (v < 0) PUT('-');
            if (!u) tmp[k++] = '0';
            while (u) { tmp[k++] = '0' + (u % 10); u /= 10; }
            while (k--) PUT(tmp[k]);
            break;
        }
        case 'l': {
            if (p[1] == 'd') {
                p++;
                long v = __builtin_va_arg(ap, long);
                char tmp[24]; int k = 0;
                unsigned long u = (v < 0) ? (unsigned long)(-v) : (unsigned long)v;
                if (v < 0) PUT('-');
                if (!u) tmp[k++] = '0';
                while (u) { tmp[k++] = '0' + (u % 10); u /= 10; }
                while (k--) PUT(tmp[k]);
            } else if (p[1] == 'u') {
                p++;
                unsigned long u = __builtin_va_arg(ap, unsigned long);
                char tmp[24]; int k = 0;
                if (!u) tmp[k++] = '0';
                while (u) { tmp[k++] = '0' + (u % 10); u /= 10; }
                while (k--) PUT(tmp[k]);
            } else {
                PUT('%'); PUT('l');
            }
            break;
        }
        case 'u': {
            unsigned int u = __builtin_va_arg(ap, unsigned int);
            char tmp[16]; int k = 0;
            if (!u) tmp[k++] = '0';
            while (u) { tmp[k++] = '0' + (u % 10); u /= 10; }
            while (k--) PUT(tmp[k]);
            break;
        }
        case 'x': {
            unsigned int u = __builtin_va_arg(ap, unsigned int);
            char tmp[16]; int k = 0;
            const char *hex = "0123456789abcdef";
            if (!u) tmp[k++] = '0';
            while (u) { tmp[k++] = hex[u & 0xF]; u >>= 4; }
            while (k--) PUT(tmp[k]);
            break;
        }
        case 'p': {
            void *v = __builtin_va_arg(ap, void*);
            unsigned long u = (unsigned long)v;
            char tmp[20]; int k = 0;
            const char *hex = "0123456789abcdef";
            PUT('0'); PUT('x');
            if (!u) tmp[k++] = '0';
            while (u) { tmp[k++] = hex[u & 0xF]; u >>= 4; }
            while (k--) PUT(tmp[k]);
            break;
        }
        case 'f': {
            double v = __builtin_va_arg(ap, double);
            if (v < 0) { PUT('-'); v = -v; }
            long ip = (long)v;
            double fp = v - (double)ip;
            char tmp[24]; int k = 0;
            if (!ip) tmp[k++] = '0';
            while (ip) { tmp[k++] = '0' + (ip % 10); ip /= 10; }
            while (k--) PUT(tmp[k]);
            PUT('.');
            for (int d = 0; d < 6; d++) {
                fp *= 10.0;
                int digit = (int)fp;
                if (digit < 0) digit = 0;
                if (digit > 9) digit = 9;
                PUT('0' + digit);
                fp -= digit;
            }
            break;
        }
        case '%':
            PUT('%');
            break;
        default:
            PUT('%');
            PUT(*p);
            break;
        }
    }
    if (cap) dst[i < cap ? i : cap - 1] = 0;
    #undef PUT
    return (int)i;
}

int printf(const char *fmt, ...) {
    char buf[2048];
    __builtin_va_list ap;
    __builtin_va_start(ap, fmt);
    int n = _format_to(buf, sizeof(buf), fmt, ap);
    __builtin_va_end(ap);
    _write_fd(1, buf, (size_t)(n < (int)sizeof(buf) ? n : (int)sizeof(buf) - 1));
    return n;
}

int snprintf(char *dst, size_t cap, const char *fmt, ...) {
    __builtin_va_list ap;
    __builtin_va_start(ap, fmt);
    int n = _format_to(dst, cap, fmt, ap);
    __builtin_va_end(ap);
    return n;
}

void abort(void) { _exit(134); }

/* ================= FILE* mínimo ================= */

typedef struct {
    int fd;
    int eof;
    int err;
} _LFile;

static _LFile _stdin_s  = { 0, 0, 0 };
static _LFile _stdout_s = { 1, 0, 0 };
static _LFile _stderr_s = { 2, 0, 0 };

void *stdin  = &_stdin_s;
void *stdout = &_stdout_s;
void *stderr = &_stderr_s;

void *fopen(const char *path, const char *mode) {
    int flags;
    int m = mode[0];
    if (m == 'r')      flags = 0;
    else if (m == 'w') flags = 1 | 64 | 512;
    else if (m == 'a') flags = 1 | 64 | 1024;
    else               return 0;
    long fd = _sys3(2, (long)path, flags, 0644);
    if (fd < 0) return 0;
    _LFile *f = (_LFile *)malloc(sizeof(_LFile));
    f->fd = (int)fd; f->eof = 0; f->err = 0;
    return f;
}

int fclose(void *fp) {
    _LFile *f = (_LFile *)fp;
    if (!f) return -1;
    if (f->fd > 2) _sys1(3, f->fd);
    return 0;
}

size_t fread(void *buf, size_t sz, size_t n, void *fp) {
    _LFile *f = (_LFile *)fp;
    if (!f || !sz || !n) return 0;
    size_t want = sz * n;
    long got = _sys3(0, f->fd, (long)buf, want);
    if (got <= 0) { f->eof = 1; return 0; }
    return (size_t)got / sz;
}

size_t fwrite(const void *buf, size_t sz, size_t n, void *fp) {
    _LFile *f = (_LFile *)fp;
    if (!f || !sz || !n) return 0;
    size_t total = sz * n;
    _write_fd(f->fd, buf, total);
    return n;
}

int fseek(void *fp, long off, int whence) {
    _LFile *f = (_LFile *)fp;
    if (!f) return -1;
    long r = _sys3(8, f->fd, off, whence);
    return r < 0 ? -1 : 0;
}

long ftell(void *fp) {
    _LFile *f = (_LFile *)fp;
    if (!f) return -1;
    return _sys3(8, f->fd, 0, 1);
}

char *fgets(char *buf, int n, void *fp) {
    _LFile *f = (_LFile *)fp;
    if (!f || n <= 0) return 0;
    int i = 0;
    while (i < n - 1) {
        char c;
        long r = _sys3(0, f->fd, (long)&c, 1);
        if (r <= 0) break;
        buf[i++] = c;
        if (c == '\n') break;
    }
    buf[i] = 0;
    if (i == 0) { f->eof = 1; return 0; }
    return buf;
}

int fputs(const char *s, void *fp) {
    _LFile *f = (_LFile *)fp;
    if (!f) return -1;
    size_t n = strlen(s);
    _write_fd(f->fd, s, n);
    return (int)n;
}

int fflush(void *fp) { (void)fp; return 0; }

/* ================= shims do Boehm GC ================= */

void GC_init(void) { }
void *GC_malloc(size_t n) { return malloc(n); }
void  GC_free(void *p)    { free(p); }

/* ================= Sockets e Epoll ================= */
/* Adaptado para a runtime freestanding do Lumina.
 * Cobre os exemplos de servidor assíncrono e http_framework.
 */

int socket(int domain, int type, int protocol) {
    return (int)_sys3(41, domain, type, protocol);
}
int bind(int fd, const void *addr, size_t len) {
    return (int)_sys3(49, fd, (long)addr, len);
}
int listen(int fd, int backlog) {
    return (int)_sys2(50, fd, backlog);
}
int accept(int fd, void *addr, void *addrlen) {
    return (int)_sys3(43, fd, (long)addr, (long)addrlen);
}
int connect(int fd, const void *addr, size_t len) {
    return (int)_sys3(42, fd, (long)addr, len);
}
/* send e recv podem usar as syscalls genéricas */
long send(int fd, const void *buf, size_t n, int flags) {
    return _sys4(44, fd, (long)buf, n, flags);
}
long recv(int fd, void *buf, size_t n, int flags) {
    return _sys4(45, fd, (long)buf, n, flags);
}
int setsockopt(int fd, int level, int optname, const void *optval, size_t optlen) {
    return (int)_sys5(54, fd, level, optname, (long)optval, optlen);
}

/* Epoll */
int epoll_create1(int flags) {
    return (int)_sys1(291, flags);
}
int epoll_ctl(int epfd, int op, int fd, void *event) {
    return (int)_sys4(233, epfd, op, fd, (long)event);
}
int epoll_wait(int epfd, void *events, int maxevents, int timeout) {
    return (int)_sys4(232, epfd, (long)events, maxevents, timeout);
}