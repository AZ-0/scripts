from typing import Callable
from idb import IDB, NotRunningException
from vm import ProxyVal
from utils import *

class Command:
    def __init__(self, names: list[str], help: str, run: Callable[[IDB, list[str]], bool]):
        self.names = names
        self.help = help
        self.run = run
        REGISTRY.append(self)

REGISTRY: list[Command] = []

def do(idb: IDB, args: list[str]):
    labels = len(idb.vm.labels)
    if idb.exec_icicle(' '.join(args)) is not None:
        return

    # Not an op and not a label
    if len(idb.vm.labels) == labels:
        print(B_RED + 'Either a comment or unparsable instruction')

def help(idb: IDB, args: list[str]):
    for arg in args or sorted(cmd.names[0] for cmd in set(idb.commands.values())):
        if arg in idb.commands:
            cmd = idb.commands[arg]
            print(B_CYAN + '• ' + '|'.join(cmd.names) + ': ' + WHITE + cmd.help)
        else:
            print(B_RED + "Unknown command: " + PINK + arg[0])

def breakpoint(idb: IDB, args: list[str]):
    bp = idb.breakpoint(''.join(args))
    print(B_BLUE+'New breakpoint at offset '+B_CYAN+f'{bp.addr}{B_BLUE} [{B_CYAN+hex(bp.addr)+B_BLUE}]: {GREEN}{idb.vm.ops[bp.addr]}')

def show(idb: IDB, args: list[str]):
    if idb.vm is None:
        raise NotRunningException(idb)

    n = 10
    if len(args) > 0:
        n = ProxyVal(idb.vm, ''.join(args[0])).eval().val

    op = idb.vm.current_op
    if not op.has_source():
        print(B_RED + 'No source attached to the current instruction')
        return
    
    d = len(str(op.source_line + n))
    for line in range(op.source_line, op.source_line + n):
        print(CYAN + f'{line:>{d}}:', WHITE + idb.vm.source[line], end='')

DO = Command(['do', ';'], 'Do icicle instruction', do)
HELP = Command(['help', 'h'], 'Display this message', help)
SHOW = Command(['show'], 'Show n (default 10) lines of code from rip onward', show)
BREAKPOINT = Command(['breakpoint', 'bp', 'b'], 'Create a breakpoint at the specified value (can be an icicle dereference) or label', breakpoint)

LOAD = Command(['load'], 'Load a file into idb', lambda idb, args: idb.load(args[0]))
RUN  = Command(['run', 'r'], 'Run the loaded file', lambda idb, _: idb.run())
NEXT = Command(['ni', 'n', ''], 'Next instruction', lambda idb, _: idb.run_once())
CONTINUE = Command(['continue', 'c'], 'Continue without stopping', lambda idb, _: idb.unhalt() or idb.vm.run_once())
EXEC = Command(['exec', '!'], 'Do python code', lambda idb, args: idb.exec_py(' '.join(args)))
STOP = Command(['stop'], 'Stop program execution', lambda idb, _: idb.vm.stop())
EXIT = Command(['exit', 'quit', 'q'], 'Exit icicle-idb', lambda *_: print(end=RESET) or exit(0))