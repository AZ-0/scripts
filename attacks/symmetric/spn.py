from abc import ABC, abstractmethod
from functools import reduce
from operator import xor

State = list[int]

def transpose(state: State) -> State:
    from math import isqrt
    n = isqrt(len(state))
    return [state[i + n*j] for i in range(n) for j in range(n)]

def bytes2state(data: bytes) -> State:
    return transpose(data)

def state2bytes(state: State) -> bytes:
    return bytes(transpose(state))

def rotate(state: State, n: int) -> State:
    """Rotate left by n"""
    return state[n:] + state[:n]

def blocks(state: State, n: int) -> list[State]:
    return [*zip(* [iter(state)] * n)]

def xors(*x: State) -> State:
    return [reduce(xor, t) for t in zip(*x)]

def sbox_inv(sbox: list[int]) -> list[int]:
    return [sbox.index(i) for i in range(len(sbox))]

class SPN(ABC):
    def __init__(self, keys: list[State]=None, sbox: list[int]=None) -> None:
        self.keys = keys
        self.sbox = sbox
        self.sbox_inv = sbox_inv(sbox) if sbox else None

    def add_round_key(self, state: State, i: int) -> State:
        return xors(state, self.keys[i])

    def substitute(self, state: State) -> State:
        return [self.sbox[s] for s in state]

    def substitute_inv(self, state: State) -> State:
        return [self.sbox_inv[s] for s in state]

    @abstractmethod
    def permute(self, state: State) -> State:
        ...

    @abstractmethod
    def permute_inv(self, state: State) -> State:
        ...

    def round(self, state: State, i: int) -> State:
        """Run the round #i, starting at #1"""
        state = self.substitute(state)
        state = self.permute(state)
        state = self.add_round_key(state, i)
        return state
    
    def round_inv(self, state: State, i: int) -> State:
        state = self.add_round_key(state, i)
        state = self.permute_inv(state)
        state = self.substitute_inv(state)
        return state

    @abstractmethod
    def final_round(self, state: State) -> State:
        ...

    @abstractmethod
    def final_round_inv(self, state: State) -> State:
        ...

    def partial_encrypt(self, state: State, rounds: int) -> State:
        state = self.add_round_key(state, 0)
        for i in range(rounds):
            state = self.round(state, i+1)
        return state

    def encrypt(self, state: State, rounds: int) -> State:
        state = self.partial_encrypt(state, rounds-1)
        state = self.final_round(state)
        return state

    def partial_decrypt(self, state: State, rounds: int) -> State:
        state = self.final_round_inv(state)
        for i in range(rounds-1, 0, -1):
            state = self.round_inv(state, i)
        return state
    
    def decrypt(self, state: State, rounds: int) -> State:
        state = self.partial_decrypt(state, rounds)
        state = self.add_round_key(state, 0)
        return state

