from sage.structure.factorization_integer import IntegerFactorization
from Crypto.Util.number import sieve_base
import time

def small_factors(n, curves=1000):
    factors = []

    for p in sieve_base:
        while n % p == 0:
            n //= p
            factors.append((p, 1))

    while n > 1:
        if is_pseudoprime(n) and is_prime(n):
            factors.append((n, 1))
            break

        t = time.time()
        try:
            res = ecm.find_factor(n, c=curves)
            if len(res) == 1:
                print("ECM fail")
                break
        except Exception as e:
            print(f"ECM fail: {e}:", *e.args)
            break

        f, m = res
        print(f"factor {f} [time: {time.time() - t}s]")
        factors.extend(factor(f))
        n = m

    return IntegerFactorization(factors)