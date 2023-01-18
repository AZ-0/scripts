from spn import State, rotate
from aes import AES

from functools import reduce
from operator import xor

def lambda_set(length: int, bound: int, fill: int=0) -> list[State]:
    return [[r] + [fill]*(length - 1) for r in range(bound)]

def is_lambda_set(states: list[State], active: list[int], bound: int):
    return all(len(set(s[i] for s in states)) == bound for i in active)

def square_attack(aes: AES, i: int, constants: list[int]=[0]):
    """Square attack on 4 rounds"""
    candidates = {*range(256)}

    for c in constants:
        pts = lambda_set(16, 256, fill=c)
        cts = [aes.encrypt(pt, 4) for pt in pts]

        candidates &= {
            k for k in range(256)
            if reduce(xor, [aes.sbox_inv[s[i] ^ k] for s in cts]) == 0
        }
    
    return candidates

if __name__ == '__main__':
    keys = [rotate([*range(16)], 2*i) for i in range(5)]
    aes = AES(keys)

    for i in range(16):
        k, = square_attack(aes, i, constants=[0, 1])
        assert k == keys[4][i]
