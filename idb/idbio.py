from collections.abc import Iterable, ByteString
from collections import deque
from typing import Any
from utils import *
import sys

class BufferedIO:
    def __init__(self, kind, log = True):
        assert kind in { 'input', 'output' }, 'BufferedIO kind can only be one of input or output'
        self.kind = kind
        self.buffer = deque()
        self.line_buffer = []
        self.log = log

    def readline(self) -> str:
        return next(self)

    def clear(self):
        self.buffer.clear()

    def _line(self, line: str, end: str):
        lines = line.split('\n')
        if len(lines) > 1 or end == '\n':
            lines[0] = ''.join(self.line_buffer) + lines[0]
            self.line_buffer.clear()

        for line in lines[:-1]:
            self.buffer.append(line)

        if end == '\n':
            self.buffer.append(lines[-1])
        else:
            self.line_buffer.append(lines[-1])
            self.line_buffer.append(end)

    def line(self, input: Any, end='\n'):
        if isinstance(input, str):
            self._line(input, end)
        elif isinstance(input, ByteString):
            self._line(input.decode('latin1'), end)
        # check for "naturally" iterable sequences
        elif isinstance(input, Iterable):
            for i in input:
                self.line(i, end)
        else:
            raise TypeError(f'Cannot naturally understand {repr(input)} as string or sequence of strings')

        return self

    def __iter__(self):
        while 1:
            try: yield next(self)
            except EOFError: raise StopIteration

    def __call__(self, *args: Any, end='\n'):
        self.line(args, end=end)

    def __iadd__(self, input):
        return self.line(input)

    def __next__(self) -> str:
        if self.buffer:
            return self.buffer.popleft()

        raise EOFError(f'Ran out of {self.kind}')

class Input(BufferedIO):
    def __init__(self, fallback = sys.stdin, log = True):
        BufferedIO.__init__(self, 'input', log=log)
        self.fallback = fallback

    def __next__(self):
        try:
            line = super().__next__()
            if self.log: print(WHITE + line + RESET, flush=True)
            return line
        except EOFError:
            if self.fallback is not None:
                print(end=WHITE, flush=True)
                line = self.fallback.readline()
                print(end=RESET, flush=True)
                return line
            raise

    def __repr__(self) -> str:
        lines = ', '.join('"' + line + '"' for line in self.buffer)
        return f"Input({lines}, then={self.fallback})"

class Output(BufferedIO):
    def __init__(self, log=True):
        BufferedIO.__init__(self, 'input', log=log)

    def _line(self, line: str, end: str):
        if self.log: print(GREY + line, end=end+RESET)
        return super()._line(line, end)
