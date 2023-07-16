def mov_attack(G, A, p, n):
    '''Find k such that A = kG, when ord G | p^n - 1 on the curve E(F_p).'''

    E = G.parent()
    E = E.change_ring(GF(p^n))
    G, A = E(G), E(A)

    ds = []
    ks = []
    n = G.order()
    while lcm(ds) < n:
        T = E.random_point()
        m = T.order()
        d = gcd(m, n)

        if d == 1:
            continue

        T *= m//d
        ds.append(d)

        g = T.weil_pairing(G, n)
        print('g =', g)

        a = T.weil_pairing(A, n)
        print('a =', a)

        k = a.log(g)
        print('k =', k)
        ks.append(k)

    k = CRT(ks, ds)
    return k