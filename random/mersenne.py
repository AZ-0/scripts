from operator import lshift, rshift
import random

# Most of this code was shamelessly stolen from StealthyDev.
# Although I did make some changes here and there and added some functions.

N = 624
M = 397
MATRIX_A   = 0x9908b0df
UPPER_MASK = 0x80000000
LOWER_MASK = 0x7fffffff

def unxorshift(x, operator, shift, mask=0xFFFFFFFF):
    res = x
    for _ in range(32):
        res = x ^ (operator(res, shift) & mask)
    return res

def untemper(random_int):
    random_int = unxorshift(random_int, rshift, 18)
    random_int = unxorshift(random_int, lshift, 15, 0xefc60000)
    random_int = unxorshift(random_int, lshift,  7, 0x9d2c5680)
    random_int = unxorshift(random_int, rshift, 11)
    return random_int

def temper(state_int):
    state_int ^= (state_int >> 11)
    state_int ^= (state_int <<  7) & 0x9d2c5680
    state_int ^= (state_int << 15) & 0xefc60000
    state_int ^= (state_int >> 18)
    return state_int

def twist(i, i1, i397_or_624):
    y = (i & 0x80000000) + (i1 & 0x7fffffff) 
    next = y >> 1
    if (y & 1) == 1:
        next ^= 0x9908b0df
    return next ^ i397_or_624

def new_state_fast(state: list[int]):
    '''Equivalent to new_state_slow, but faster'''
    mt = state.copy()
    for i in range(N):
        y = (mt[i] & UPPER_MASK) | (mt[i+1] & LOWER_MASK)
        z = mt[(i + M) % N] ^ (y >> 1) ^ (y & 1)*MATRIX_A
        mt[i] = z
    return mt

def new_state_slow(state: list[int]):
    '''Equivalent to new_state_fast, but the code is easier to understand for cracking purposes'''
    mt = state.copy() + [0]*N
    for i in range(N):
        y = (mt[i] & UPPER_MASK) | (mt[i+1] & LOWER_MASK)
        z = mt[i + M] ^ (y >> 1) ^ (y & 1)*MATRIX_A
        mt[i + N] = z
    return mt[-N:]

def randbits_to_uints(n: int, bits):
    assert n.bit_length() <= bits
    uints = [(n >> i) % 2**32 for i in range(0, bits, 32)]

    if bits % 32:
        uints[-1] <<= 32 - bits % 32
        assert uints[-1] < 2**32 # this lends some credence that this part of the code isn't broken

    return uints

def uints_to_randbits(uints, bits):
    L = len(uints) - 1
    n = 0
    for i in range(L):
        n |= uints[i] << 32*i

    u = uints[-1]
    if bits%32:
        u >>= (32 - bits%32)

    return n | u << 32*L

def setstate(leaks):
    assert len(leaks) == 624
    random.setstate((3, tuple([*map(untemper, leaks), 624]), None))
