def PH_partial(h, g, p, fact_phi):
    """Returns (x, m), where
    - x is the dlog of h in base g, mod m
    - m = lcm(pi^ei) for (pi, ei) in fact_phi
    """
    res = []
    mod = []
    k = GF(p)

    phi = p-1
    for pi, ei in fact_phi:
        gi = pow(g, phi//(pi^ei), p)
        hi = pow(h, phi//(pi^ei), p)
        xi = discrete_log_lambda(k(hi), k(gi), bounds = (0, pi^ei))
        res.append(int(xi))
        mod.append(int(pi^ei))

    x, m = CRT(res, mod), lcm(mod)
    assert pow(g, x * phi//m, p) == pow(h, phi//m, p)
    return x, m