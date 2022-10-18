# sage

def dlog_power_of_2(h, g, p):
    """Returns (x, m) where
       - x is the dlog of h in base g, mod m
       - m = 2^v2(ord g)
    """
    k = (p - 1).valuation(2)
    g = pow(g, (p - 1) >> k, p) # map onto subgroup of order m
    h = pow(h, (p - 1) >> k, p)

    m = 1 << k
    while pow(g, m >> 1, p) == 1:
        m >>= 1

    bits = []
    for i in range(k):
        bits.append(0 if pow(h, m >> i+1, p) == 1 else 1)
        h *= pow(g, -bits[-1] << i, p)

    return sum(b << i for i, b in enumerate(bits)), m


# pure python

def dlog_power_of_2(h, g, p):
    """Returns (x, m) where
       - x is the dlog of h in base g, mod m
       - m = 2^v2(ord g)
    """
    def v2(n):
        assert n > 0
        v = 0
        while n & 1 == 0:
            v += 1
            n >>= 1
        return v

    k = v2(p - 1)
    g = pow(g, (p - 1) >> k, p)
    h = pow(h, (p - 1) >> k, p)

    m = 1 << k
    while pow(g, m >> 1, p) == 1:
        m >>= 1

    bits = []
    for i in range(k):
        bits.append(0 if pow(h, m >> i+1, p) == 1 else 1)
        h = h * pow(g, -bits[-1] << i, p) % p

    return sum(b << i for i, b in enumerate(bits)), m
