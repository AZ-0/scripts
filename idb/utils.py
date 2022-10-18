from string import whitespace
from typing import Generic, TypeVar

RESET  = '\x1b[0m'
BLACK  = '\x1b[30m'
RED    = '\x1b[31m'
GREEN  = '\x1b[32m'
YELLOW = '\x1b[33m'
BLUE   = '\x1b[34m'
PINK   = '\x1b[35m'
CYAN   = '\x1b[36m'
WHITE  = '\x1b[37m'
GREY   = '\x1b[90m'
B_RED   = '\x1b[91m'
B_GREEN = '\x1b[92m'
B_BLUE  = '\x1b[94m'
B_PINK  = '\x1b[95m'
B_CYAN  = '\x1b[96m'
B_WHITE = '\x1b[97m'

def identity(x):
    return x

def as_bytes(x):
    if isinstance(x, bytes): return x
    return str(x).encode()

def bytes_to_long(b: bytes) -> int:
    return int.from_bytes(b, 'big')

def long_to_bytes(n: int) -> bytes:
    return n.to_bytes((n.bit_length() + 7) // 8, 'big') or b'\0'

def safesplit(s: str, sep: str = None, n: int = None, keep_empty: bool = True) -> list[str]:
    def sepstart(x: str) -> tuple[bool, int]:
        if sep is not None: return x.startswith(sep), len(sep)
        y = x
        while y and y[0] in whitespace: y = y[1:]
        return len(y) != len(x), len(x) - len(y)
    instr = False
    parts = []
    i = start = 0
    while i < len(s):
        if s[i] == '"': instr = not instr
        elif s[i] == '\\' and s[i+1] == '"': i += 1
        elif not instr:
            is_sep, L = sepstart(s[i:])
            if is_sep:
                if keep_empty or start != i: parts.append(s[start:i])
                i = start = i+L
                if n is not None and (n := n-1) <= 0:
                    break
                continue
        i += 1

    if keep_empty or start < len(s): parts.append(s[start:])
    return parts


VT = TypeVar("VT")

class AccessDict(dict[str, VT]):
    def __getattribute__(self, name: str) -> VT:
        if name in self:
            return self[name]

        return super().__getattribute__(name)