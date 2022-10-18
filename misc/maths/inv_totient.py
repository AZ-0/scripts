def inv_totient(t, ds): # find a multiple of the inverse of the totient
    candidates = []
    for d in ds:
        if is_pseudoprime(d+1):
            candidates.append(d+1)

    n = factor(1)
    for p in candidates:
        tt = t//(p - 1)
        n *= p
        while tt%p == 0:
            n *= p
            tt //= p

    return n