from vm import VM, Op, store_left_evaled
from memory import Kind, Cell, ProxyMemory

from breakpoint import Breakpoint
from idbio import Input, Output
from utils import *

from typing import Callable, Union, Any
from functools import wraps
from enum import Enum, auto
import builtins

T = TypeVar('T')

class State(Enum):
    '''State of IDB.'''
    NOT_RUNNING = auto()
    CONTINUE    = auto()
    BREAKPOINT  = auto()

class NotRunningException(Exception):
    '''Exception thrown when trying to perform an operation that requires a running program, but no program is running.'''
    def __init__(self, idb, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.idb: IDB = idb

def assert_running(method: Callable[[Any], T]):
    '''When the method is called, check whether the program is running and raise NotRunningException if not.'''
    @wraps(method)
    def decorator(idb: 'IDB', *args, **kwargs) -> T:
        if idb.state == State.NOT_RUNNING:
            raise NotRunningException(idb)
        return method(idb, *args, **kwargs)
    return decorator

class IDB:
    '''An ICICLE debugger'''
    def __init__(self):
        from commands import Command, REGISTRY # local import to prevent cyclic dependency
        self.state: State = State.NOT_RUNNING
        self.input: Input = Input()
        self.output: Output = Output()
        self.file: str = None
        self.vm: VM = None
        self.commands: dict[str, Command] = {}
        self.breakpoints: list[Breakpoint] = []
        self.vars: dict[str, Any] = {}

        for cmd in REGISTRY:
            self.register_cmd(cmd)

    def register_cmd(self, cmd):
        '''Registers the given command to self.'''
        for name in cmd.names:
            self.commands[name] = cmd

    def breakpoint(self, ref: Union[str, int]) -> Breakpoint:
        bp = Breakpoint(self.vm, ref)
        self.breakpoints.append(bp)
        return bp

    @assert_running
    def exec_icicle(self, instruction: str) -> Op:
        '''Parses the given ICICLE line into an op for the current vm, executes it, and returns it'''
        op = self.vm.parse_line(instruction)
        if op is not None: op()
        return op

    @assert_running
    def exec_py(self, code: str):
        '''Executes python code, with extended environment (pwntools, math, and utils are globals).
        Other declared variables:
            - idb: the debugger (not reassignable)
            - mem: the memory (not reassignable)
            - r0 -> r15 | rip: the registers
        '''
        import math, pwn, utils

        env = vars(pwn) | vars(builtins) | vars(math) | vars(utils) \
            | { 'idb': self, 'vm': self.vm, 'mem' : ProxyMemory(self.vm.memory) } \
            | { reg: dummy.val for reg, dummy in self.vm.regs.items() }

        exec(code, env, self.vars)

        for reg, dummy in self.vm.regs.items():
            dummy.val = self.vars.pop(reg, env[reg])

        for var in 'idb', 'mem', 'vb':
            if var in self.vars:
                print(B_RED + var +' is not reassignable')
                del self.vars[var]

    def load(self, file: str):
        '''Loads a file into a VM'''
        with open(file) as f:
            self.vm = VM.from_file(f)
        self.file = file

    def run(self, state=State.CONTINUE):
        '''Resets the vm and its input/output, then run self with the given state.'''
        self.vm.reset()
        self.vm.running = True
        Op.op_readstr = store_left_evaled(lambda: next(self.input).encode('latin1'))
        Op.op_readint = store_left_evaled(lambda: int(next(self.input)))
        Op.op_pr = lambda _, x: self.output.line(as_bytes(x.eval().val).decode('latin1'), end='')

        self.state = state
        self.debug = Debug(self.vm, self)

    @assert_running
    def run_once(self):
        self.vm.run_once()

    def unhalt(self):
        '''Continue the execution'''
        self.state = State.CONTINUE

    def update_halt(self):
        if self.state == State.NOT_RUNNING:
            return

        if self.state != State.BREAKPOINT:
            for i, bp in enumerate(self.breakpoints):
                if bp.is_hit():
                    self.state = State.BREAKPOINT
                    print(B_PINK + f'Hit breakpoint #{i}: {bp}' + RESET)
                    break

        if not self.vm.running and self.state != State.NOT_RUNNING:
            print(B_PINK + 'The vm has stopped')
            self.state = State.NOT_RUNNING

    def is_halted(self) -> bool:
        return self.state is not State.CONTINUE

    def wait_cmd(self):
        cmd = safesplit(input(GREEN + "$ "), keep_empty=False)

        try:
            if not cmd:
                self.commands[''].run(self, cmd[1:])
            elif cmd[0] in self.commands:
                self.commands[cmd[0]].run(self, cmd[1:])
            else:
                print(B_RED + "Unknown command: " + B_PINK + cmd[0])
        except NotRunningException:
            print(B_RED+'No program is currently running!')

    def cli(self):
        while 1:
            self.update_halt()

            if self.is_halted():
                if self.state != State.NOT_RUNNING:
                    self.debug(self.vm.current_op)
                self.wait_cmd()
            else:
                self.vm.run_once()

            print(end=RESET)

class Debug:
    def __init__(self, vm: VM, idb: IDB) -> None:
        self.vm = vm
        self.idb = idb
        self.regs = { f"r{i}": 0 for i in range(16) } | {"rip": 0}
        self.last_op: Op = None

    def format_val(self, val):
        if isinstance(val, int):
            return f'0x{val:0>8x}' if val >= 0 else f'-0x{-val:0>7x}'
        return str(val)

    def format_reg_val(self, reg: str, dummy: Cell, trace: list[Cell] = []):
        fval = self.format_val(dummy.val)
        if dummy.kind is Kind.CODE and dummy.val < len(self.vm.ops):
            return f'{RED}{fval}{WHITE} -> {GREEN}{self.vm.ops[dummy.val]}{WHITE}'

        if dummy.kind is Kind.MEMORY and dummy.val < len(self.vm.memory):
            if dummy in trace:
                return BLUE + '[loop]'
            return BLUE + fval + WHITE + ' -> ' + self.format_reg_val(reg, self.vm.memory[dummy.val], trace = trace + [dummy])

        return CYAN + fval

    def print_reg(self, reg):
        print(WHITE if self.regs[reg] == self.vm.regs[reg].val else YELLOW, end='')
        print(f'   {reg+":":<5}{WHITE}', end='')
        print(self.format_reg_val(reg, self.vm.regs[reg]))

    def print_stack(self):
        print(PINK + 'Stack Frame:')
        rsp = self.regs['r14']
        for block in range(rsp, rsp+50, 8):
            print(f'   {BLUE}0x{block:0>6x}: ', end='')
            for addr in range(block, block+8):
                val = self.vm.memory[addr].val
                print((GREY if val == 0 else WHITE) + self.format_val(val), end=' ')
            print(RESET)

    def __call__(self, op: Op = None, next: bool = False):
        if not self.idb.is_halted(): return
        if op is not None:
            print(f"{PINK}Executing: {GREEN}{op}")

        print(PINK + 'Registers:')
        for reg in self.vm.regs:
            self.print_reg(reg)
            self.regs[reg] = self.vm.regs[reg].val

        self.print_stack()

if __name__ == '__main__':
    IDB().cli()
