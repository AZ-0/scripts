from abc import ABC, abstractmethod

State = list[int]

def transpose(state: State, n: int=4) -> State:
    return [state[i + n*j] for i in range(n) for j in range(n)]

def bytes2states(data: bytes, n: int=4) -> State:
    return transpose(data)

def state2bytes(state: State, n: int=4) -> bytes:
    return bytes(transpose(state, n=n))

def rotate(state: State, n: int) -> State:
    return state[n:] + state[:n]

def blocks(state: State, n: int) -> list[State]:
    return [*zip(* [iter(state)] * n)]

class SPN(ABC):
    def __init__(self, keys: list[State]=None, sbox: list[int]=None) -> None:
        self.keys = keys
        self.sbox = sbox
        self.sbox_inv = [sbox.index(i) for i in range(len(sbox))] if sbox else None

    def add(self, s, k):
        return s ^ k

    def add_round_key(self, state: State, i: int) -> State:
        return [self.add(s, k) for s, k in zip(state, self.keys[i])]

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

