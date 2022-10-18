from utils import identity

from typing import Any, Callable, Iterable, Iterator, List, TypeVar, Generic
from dataclasses import dataclass
from functools import partial
from enum import Enum

MAGIC_OVERLOAD = [ '__or__', '__and__', '__xor__', '__add__', '__sub__', '__mod__', '__mul__', '__div__', '__floordiv__' ]

class Kind(Enum):
    vars().update({ x : lambda self, *args, **kwargs: getattr(self, x)(*args, **kwargs) for x in MAGIC_OVERLOAD })

    '''The kind of a Cell'''
    def __init__(self, *args, **kwargs) -> None:
        Enum.__init__(*args, **kwargs)
        overload: Callable[[Kind, Kind], Kind] = partial(self.value[0], self)

        for method in MAGIC_OVERLOAD:
            setattr(self, method, overload)

    def __repr__(self) -> str:
        return f'Kind[{self.name}]'

    def __str__(self) -> str:
        return self.name.capitalize()

    def rev(self) -> 'Kind':
        return self

    def intstr(self) -> 'Kind':
        return Kind.VALUE
    
    def strint(self) -> 'Kind':
        return Kind.VALUE

    VALUE  = [lambda _, b: b]
    CODE   = [lambda a, _: a]
    MEMORY = [lambda a, _: a]

T = TypeVar('T')
U = TypeVar('U')

@dataclass
class Cell(Generic[T]):
    val: T
    kind: Kind = Kind.VALUE

    def copy(self: 'Cell[T]') -> 'Cell[U]':
        return Cell(self.val, self.kind)

    def map(self: 'Cell[T]', f: Callable[[T], U], kindmap: Callable[[Kind], Kind] = identity) -> 'Cell[U]':
        return Cell(f(self.val), kindmap(self.kind))

    def __iter__(self) -> Iterable[Any]:
        return iter((self.val, self.kind))

    def __str__(self) -> str:
        return f'Cell(val={self.val}, kind={self.kind})'

class ProxyMemory(List):
    def __init__(self, proxy):
        self.proxy: list[Cell] = proxy

    def __iter__(self):
        return (cell.val for cell in self.proxy)

    def __len__(self) -> int:
        return len(self.proxy)

    def __setitem__(self, where: slice, value: int):
        if isinstance(ref := self.proxy[where], Cell):
            ref.val = value

        for cell, val in zip(ref, value):
            cell.val = val

    def __getitem__(self, where: slice):
        if isinstance(ref := self.proxy[where], Cell):
            return ref.val
        return [cell.val for cell in ref]

    def __reversed__(self) -> Iterator[int]:
        return reversed(list(self))

    def __repr__(self) -> str:
        return repr(list(self))

    def clear(self) -> None:
        for cell in self.proxy:
            cell.val = 0

    def copy(self) -> list[int]:
        return list(self)

    def index(self, value) -> int:
        for i, val in enumerate(self):
            if value == val:
                return i

        raise ValueError(f'{value} is not in list')

    def count(self, value) -> int:
        count = 0
        for val in self:
            if val == value:
                count += 1
        return count

    def reverse(self) -> None:
        self.proxy.reverse()

    def sort(self, key: Callable[[int], int] = None, reverse: bool = False) -> None:
        key = key or identity
        self.proxy.sort(key = lambda c: key(c.val), reverse = reverse)
