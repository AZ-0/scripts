load('order_factored.sage')


def _csidh_action(E, order, n, facs):
    """
    Internal function. Use "csidh_action" instead.
    """
    k = order.prime_to_m_part(n)

    while n > 1:
        # print('.', end='', flush=True)
        P = k*E.random_point()
        o = order_factored(P, order, facs) # much faster than P.order()
        P._order = o

        d = gcd(n, o)
        P *= o//d
        n //= d

        if P.is_zero():
            continue

        # print('\nP:', P)
        # print('d:', d)
        E = E.isogeny(P, algorithm='factored', check=False).codomain()
        # print('E:', -E.montgomery_model().defining_polynomial()(z=1))

    return E


def _dual_action(E, order, n, facs):
    """Internal function. Use "csidh_action" instead."""
    E_ = E.quadratic_twist()
    E_ = _csidh_action(E_, order, n, facs)
    return E_.quadratic_twist()


def csidh_action(E, es, p_facs=None, order=None):
    """
    Return the codomain of the unique isogeny of degree prod(qi^ei) starting from E.

    INPUT:

    * "E" -- elliptic curve

    * "es" -- list of integers: (ei)

    * "p_facs" (optional) -- list of integers: some prime factors (qi) of p+1 (default: every prime factor besides 2)

    * "order" (optional) -- order of E

    OUTPUT:

    * An elliptic curve
    """
    _old_proof = proof.all()

    # print('-'*20)
    # print(f'CSIDH ACTION for {E}')
    # print('exponents:', es)

    if p_facs is None:
        p = E.base_field().characteristic()
        p_facs = [ q for q,_ in factor(p+1) if q != 2 ]
    # print('p factors:', p_facs)
    assert len(p_facs) == len(es)

    if order is None:
        order = E.order()

    pos_n, pos_facs = 1, []
    neg_n, neg_facs = 1, []
    for qi, ei in zip(p_facs, es):
        if ei > 0:
            pos_n *= qi**ei
            pos_facs.append(qi)
        else:
            neg_n *= qi**-ei
            neg_facs.append(qi)

    E = _csidh_action(E, order, pos_n, pos_facs)
    E = _dual_action(E, order, neg_n, neg_facs)
    E = E.montgomery_model()

    proof.all(_old_proof)
    return E

if __name__ == '__main__':
    E0 = EllipticCurve(GF(419), [1, 0])
    E1 = csidh_action(E0, [2,3,4])
    E2 = csidh_action(E1, [-2,-3,-4])
    print('-'*20)
    print('E0:', E0)
    print('E1:', E1)
    print('E2:', E2)
    assert E0 == E2 # in the Montgomery model
