def find_factor(N, m):
    '''Find a factor of N, given a multiple m of λ(N)'''
    v = m.valuation(2)
    
    for a in primes(isqrt(N)):
        for k in range(1, v + 1):
            g = gcd(pow(a, m >> k, N).lift() - 1, N)
            if 1 < g < N:
                return g

    print('Found no factor!')


def factorize(N, m):
    '''Factorize N, given a multiple m of λ(N)'''
    from sage.structure.factorization_integer import IntegerFactorization
    if is_prime(N):
        return IntegerFactorization([(N, 1)])

    n, e = N.perfect_power()
    if e > 1:
        return IntegerFactorization(factorize(n)^e)

    X = find_factor(N, m)
    return IntegerFactorization(factorize(X, m) * factorize(N//X, m))

