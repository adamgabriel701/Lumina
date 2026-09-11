import os
import re
import hashlib

LUMINA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STD_DIR = os.path.join(LUMINA_ROOT, "std")

class Color:
    RESET       = '\033[0m'
    BOLD        = '\033[1m'
    DIM         = '\033[2m'
    UNDERLINE   = '\033[4m'
    BLINK       = '\033[5m'

    BLACK       = '\033[30m'
    RED         = '\033[31m'
    GREEN       = '\033[32m'
    YELLOW      = '\033[33m'
    BLUE        = '\033[34m'
    MAGENTA     = '\033[35m'
    CYAN        = '\033[36m'
    WHITE       = '\033[37m'

    BRIGHT_BLACK   = '\033[90m'
    BRIGHT_RED     = '\033[91m'
    BRIGHT_GREEN   = '\033[92m'
    BRIGHT_YELLOW  = '\033[93m'
    BRIGHT_BLUE    = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN    = '\033[96m'
    BRIGHT_WHITE   = '\033[97m'

    ERROR   = BRIGHT_RED
    SUCCESS = BRIGHT_GREEN
    WARN    = BRIGHT_YELLOW
    INFO    = BRIGHT_CYAN
    STEP    = BRIGHT_MAGENTA
    HEADER  = BOLD + BRIGHT_BLUE
    ARROW   = BRIGHT_CYAN
    PROMPT  = BOLD + BRIGHT_CYAN
    MUTED   = BRIGHT_BLACK

def paint(text, color):
    return f"{color}{text}{Color.RESET}"

def cprint(*args, color=Color.RESET, end='\n', sep=' '):
    text = sep.join(str(a) for a in args)
    print(f"{color}{text}{Color.RESET}", end=end)

def info(msg):    cprint(msg, color=Color.INFO)
def success(msg): cprint(msg, color=Color.SUCCESS)
def warn(msg):    cprint(msg, color=Color.WARN)
def error(msg):   cprint(msg, color=Color.ERROR)
def step(msg):    cprint(msg, color=Color.STEP)
def header(msg):  cprint(msg, color=Color.HEADER)
def arrow(msg):   cprint(msg, color=Color.ARROW)

def get_all_dependency_files(filename):
    files = set()
    def resolve(f):
        abs_f = os.path.abspath(f)
        if abs_f in files:
            return
        files.add(abs_f)
        try:
            with open(f, "r") as file:
                code = file.read()
        except Exception:
            return

        for match in re.finditer(r'import\s+"([^"]+)"', code):
            dep = match.group(1)
            if dep.startswith("std/"):
                dep_path = os.path.join(STD_DIR, dep.replace("std/", "") + ".lm")
            elif os.path.exists(dep + ".lm" if not dep.endswith(".lm") else dep):
                dep_path = dep if dep.endswith(".lm") else dep + ".lm"
            else:
                dep_path = os.path.join("lumina_modules", dep)
                if not dep_path.endswith(".lm"):
                    dep_path += ".lm"
            resolve(dep_path)

    resolve(filename)
    return list(files)

def get_cache_hash(filename):
    hasher = hashlib.md5()
    deps = get_all_dependency_files(filename)
    for f in sorted(deps):
        try:
            with open(f, "rb") as file:
                hasher.update(file.read())
        except Exception:
            pass
    return hasher.hexdigest()