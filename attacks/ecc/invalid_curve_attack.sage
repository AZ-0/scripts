from scripts.attacks.factoring.partial import small_factors

def low_order_points(p, a, bound):
    '''Find points of order lower than `bound` on invalid curves y² = x³ + ax + b (mod `p`)'''
    b = 0
    primes = []

    while 1:
        print('.', end='')
        b += 1
        R = EllipticCurve(GF(p), [a, b]).random_point()
        o = R.order()

        for (q, v) in small_factors(o):
            if q > bound or q in primes:
                continue

            primes.append(q)

            e = min(v, int(log(bound, q)))
            m = q^e
            print(f'\nm = {q}^{e}')

            X = (o//m)*R
            yield m, X

