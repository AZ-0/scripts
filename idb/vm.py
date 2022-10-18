#!/usr/bin/python3
from utils import as_bytes, bytes_to_long, long_to_bytes, safesplit, identity, AccessDict
from memory import Kind, Cell

from itertools import cycle
from typing import Any, Callable, TextIO

import ast, operator, random

def equalize(a: Cell, b: Cell, conv=as_bytes) -> tuple[Cell, Cell]:
    if type(a.val) == type(b.val): return a, b
    if not isinstance(a.val, bytes): return a.map(conv), b
    if not isinstance(b.val, bytes): return a, b.map(conv)
    return a, b

class ProxyVal:
    def __init__(self, vm: 'VM', arg: str):
        self.vm = vm
        self.arg = arg
        self.storable = arg in self.vm.regs

        if arg[0] == '[':
            assert arg[-1] == ']', 'Malformed dereference (expected closing ] but none found)'
            self.storable = True
            self.deref = ProxyVal(vm, arg[1:-1])

    def eval(self) -> Cell:
        if self.arg in self.vm.labels:
            return Cell(self.vm.labels[self.arg])

        if   self.arg[0] == 'r': return self.vm.regs[self.arg]
        elif self.arg[0] == '[': return self.vm.memory[self.deref.eval().val]

        r = ast.literal_eval(self.arg)
        if isinstance(r, int):
            return Cell(r)

        return Cell(as_bytes(r))

    def store(self, val: Cell):
        assert self.storable

        if self.arg[0] == 'r':
            self.vm.regs[self.arg] = val
            if self.arg == 'r14': self.vm.regs[self.arg].kind = Kind.MEMORY
            if self.arg == 'rip': self.vm.regs[self.arg].kind = Kind.CODE
        else:
            self.vm.memory[self.deref.eval().val] = val

    def __str__(self) -> str:
        return str(self.arg)

    def __repr__(self) -> str:
        return f'Proxy[{self.arg}]'

def wrap(f):
    def wrapped(_, r: ProxyVal, x: ProxyVal, y: ProxyVal):
        a, b = equalize(x.eval(), y.eval())
        r.store(Cell(f(a.val, b.val), f(a.kind, b.kind)))
    return wrapped

def cjump(cond):
    def f(self: 'Op', *args: ProxyVal):
        if cond(*[arg.eval().val for arg in args[:-1]]):
            self.vm.rip = args[-1].eval().val - 1
    return f

def store_left_evaled(func: Callable[[Cell], Any]):
    def f(_: 'Op', r: ProxyVal, *args: ProxyVal):
        res = func(*[x.eval() for x in args])
        if type(res) in [int, bytes]:
            r.store(Cell(res))
        else:
            r.store(Cell(*res))

    return f

def xor(a: ProxyVal, b: ProxyVal):
    def _xor(a, b):
        if isinstance(a, int): return a ^ b
        a, b = sorted([a, b], key=len)
        return bytes(x ^ y for x, y in zip(cycle(a), b))

    x, y = equalize(a, b, long_to_bytes)
    return Cell(_xor(x.val, y.val), x.kind ^ y.kind)

class Op:
    def __init__(self, vm: 'VM', op: str, args: str, source_line: int = None):
        self.vm = vm
        self.op = op
        self.args = [ProxyVal(vm, arg) for arg in args]
        self.source_line = source_line

    def has_source(self) -> bool:
        return self.source_line is not None

    def getcall(self):
        return getattr(self, f'op_{self.op}')

    def __call__(self):
        self.getcall()(*self.args)

    def __str__(self) -> str:
        return f"{self.op} {', '.join(map(str, self.args))}"

    def __repr__(self) -> str:
        return f'{self.op}'

    op_add  = wrap(operator.add)
    op_sub  = wrap(operator.sub)
    op_mult = wrap(operator.mul)
    op_div  = wrap(operator.floordiv)
    op_mod  = wrap(operator.mod)
    op_and  = wrap(operator.and_)
    op_or   = wrap(operator.or_)

    op_xor = store_left_evaled(xor)
    op_rev = store_left_evaled(lambda a: [as_bytes(a.val)[::-1], a.kind.rev()])
    op_mov = store_left_evaled(identity)
    op_strint = store_left_evaled(lambda a: [bytes_to_long(a.val), a.kind.strint()])
    op_intstr = store_left_evaled(lambda a: [long_to_bytes(a.val), a.kind.intstr()])

    op_pr = lambda _, x: print(as_bytes(x.eval().val).decode('latin1'), end="")

    op_readstr = store_left_evaled(lambda: input().encode('latin1'))
    op_readint = store_left_evaled(lambda: int(input()))

    op_j   = cjump(lambda: True)
    op_jnz = cjump(lambda x: x != 0)
    op_jz  = cjump(lambda x: x == 0)
    op_jl  = cjump(lambda a, b: a < b)

    op_randbyte = store_left_evaled(lambda *_: random.randrange(256))
    op_flag = store_left_evaled(lambda *_: open('test/flag.txt', 'rb').read())

class VM:
    from string import ascii_letters as LABEL_ALPHA
    LABEL_ALPHA = set(LABEL_ALPHA) | { '_' }
    REGISTER_NAMES = [f'r{i}' for i in range(16)] + ['rip']

    def __init__(self, instructions: list[Op], *, source: list[str] = None):
        self.ops = instructions
        self.source = source
        self.labels = AccessDict[int]()
        self.registers = self.regs = AccessDict[Cell]({ f'r{i}': Cell(0) for i in range(16) } | { 'rip' : Cell(-1) })
        self.running = False
        self.memory: list[Cell]
        self.reset()

    def parse_line(self, line: str, line_nb: int = 0) -> tuple[Op, dict[str, int]]:
        line = safesplit(line, '#', 1)[0]
        if not line.strip():
            return None, {}

        line = ' '.join(safesplit(line.strip()))
        op, args = safesplit(line + ' ', ' ', 1)
        if line.strip().endswith(':'):
            label = line[:-1]
            assert all(c in VM.LABEL_ALPHA for c in label) and label not in VM.REGISTER_NAMES, 'Label must be alphanumeric and not be a register name'
            return None, { label : line_nb }

        return Op(self, op, safesplit(args.strip(), ', ')), {}

    def parse(self, lines: list[str]) -> tuple[list[Op], dict[str, int], list[str]]:
        ops: list[Op] = []
        labels: dict[str, int] = {}
        source: list[str] = []

        for line in lines:
            op, label = self.parse_line(line, len(self.ops) + len(ops))
            labels |= label

            if op is not None:
                ops.append(op)
                op.source_line = len(source) + len(self.source or [])

            if op is not None or label:
                source.append(line)

        return ops, labels, source

    @staticmethod
    def from_file(file: TextIO) -> 'VM':
        vm = VM([])
        vm.ops, labels, vm.source = vm.parse(file.readlines())
        vm.labels |= labels
        return vm

    @property
    def rip(self) -> int:
        return self.regs.rip.val

    @rip.setter
    def rip(self, val: int):
        self.regs.rip.val = val

    @property
    def current_op(self) -> Op:
        return self.ops[self.rip] if self.rip < len(self.ops) else None

    @property
    def next_op(self) -> Op:
        return self.ops[self.rip + 1] if self.rip + 1 < len(self.ops) else None

    def reset(self):
        self.memory = [Cell(0) for _ in range(1 << 16)]

        for cell in self.regs.values():
            cell.val = 0
            cell.kind = Kind.VALUE

        self.regs.rip.kind = Kind.CODE
        self.regs.r14.kind = Kind.MEMORY
        self.regs.r15.kind = Kind.MEMORY

    def run_once(self) -> None:
        self.current_op()
        self.rip += 1
        self.running &= 0 <= self.rip < len(self.ops)

    def run(self) -> None:
        self.running = True
        while self.running:
            self.run_once()

    def stop(self) -> None:
        self.running = False
