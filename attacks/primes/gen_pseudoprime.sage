from itertools import product
from tqdm import tqdm, trange

from misc.miller_rabin import miller_rabin

# https://eprint.iacr.org/2018/749.pdf, Appendix A

def get_Sa(a):
    '''Compute S_a for a prime a'''
    if a == 2:
        return { 3, 5 }

    R = set(quadratic_residues(a)) - {0}
    NR = set(range(1, a)) - set(R)
    return { crt([r, 1], [a, 4]) for r in NR } | { crt([r, 3], [a, 4]) for r in (R if a % 4 == 3 else NR) }

def inter_k(a, Sa, k):
    return set.intersection(*[
        { inverse_mod(ki, 4*a) * (x + ki - 1) % (4*a) for x in Sa }
            for ki in k
    ])

def find_coprime(s, a, b):
    # Find a number x that is coprime to set s with x in [a,b]
    while True:
        x = randint(a, b)
        if all(gcd(x, a) == 1 for a in s):
            return x

def generate_k(A, S):
    while True:
        k = [1]
        for _ in range(2):
            k.append(find_coprime(A + k, max(A), max(A) * 10)) # k only needs to be coprime to A and k

        ksaks = []
        for a in A:
            ksak = inter_k(a, S[a], k)
            ksaks.append(sorted(list(ksak)))

        if all(len(l) > 0 for l in ksaks):
            break
    
    return k, ksaks

def random_residues(ksaks):
    ksak, *ksaks = ksaks
    res = choice(ksak)
    try:
        return [res] + [
            choice([r for r in ksak if r%4 == res%4])
            for ksak in ksaks
        ]
    except IndexError:
        return None

def search_pseudo_prime(A, k, ksaks, bits = None):
    moduli = [4*b for b in A] + k[1:]
    kinvs = [inverse_mod(-k[2], k[1]), inverse_mod(-k[1], k[2])]
    L = lcm(moduli)

    for _ in range(10000):
        residues = random_residues(ksaks)
        if residues is None:
            return None
        
        p0 = crt(residues + kinvs, moduli)
        assert gcd(p0, L) == 1
        
        print(residues)
        print(f'p = {p0} mod {L}')

        if bits:
            p0 += (2^(bits // 3))//L * L

        for _ in tqdm(range(100000)):
            p0 += L
            if is_pseudoprime(p0):
                p1 = k[1] * (p0 - 1) + 1
                p2 = k[2] * (p0 - 1) + 1
                if is_pseudoprime(p1) and is_pseudoprime(p2) and miller_rabin(p0*p1*p2, A):
                    n = p0 * p1 * p2
                    print('n =', n)
                    print('p =', (p0, p1, p2))
                    return n, (p0, p1, p2)

def generate_pseudoprime(base, bits=None):
    A = base
    S = { a : get_Sa(a) for a in A }

    while True:
        k, ksaks = generate_k(A, S)
        x = search_pseudo_prime(A, k, ksaks, bits=bits)
        if x is None:
            print('retry')
            continue

        n, ps = x
        print('bits =', n.nbits())
        break