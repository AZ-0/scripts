from itertools import product
from spiral import Spiral
from utils import bytes2matrix, matrix2bytes, SBOX
from math import prod
from tqdm import tqdm

spi = Spiral([*range(16)], rounds=4)
INV_SBOX = [SBOX.index(i) for i in range(255)]

def oracle(pt):
    io.sendlineafter('>>>', '2')
    io.sendline(bytes(pt).hex())
    return bytes2matrix(bytes.fromhex(io.recvline(False).decode()))
    #return bytes2matrix(spi.encrypt(pt))

def delta_set():
    return [[i] + [0]*15 for i in range(255)] # Spiral is mod 255 instead of 256

def delta_cts():
    return [oracle(pt) for pt in tqdm(delta_set())]

def key_candidates(cts):
    keys = [[] for _ in range(16)]
    for i, j in product(range(4), repeat=2):
        for k in range(255):
            s = sum(INV_SBOX[(ct[i][j] - k) % 255] for ct in cts)
            if s % 255 == 0:
                keys[4*i+j].append(k)
                print(f'{i, j}: {k = }')

    return keys

def attack(cts):
    candidates = key_candidates(cts)
    print(f'Found {prod(len(k) for k in candidates)} candidates')

    pt = delta_set()[0]
    ct = cts[0]

    keys = []
    for key in product(*candidates):
        if bytes2matrix(Spiral(key, rounds=4).encrypt_block(pt)) == ct:
            print('key =', key)
            keys.append(key)

    return keys

from pwn import remote, context

io = remote('spiral.ctf.maplebacon.org', 1337)
io.sendlineafter('>>> ', '1')
enc = bytes.fromhex(io.recvline(False).decode())
cts = delta_cts()
keys = attack(cts)

for key in keys:
    print('dec =', Spiral(key, rounds=4).decrypt(enc))
