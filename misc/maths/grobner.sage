def canonical_form(f, G):
    '''Returns the canonical form of f with respect to the ideal generated by the Gröbner basis G.
    This implements Buchberger reduction.'''
    h = 0
    while f != 0:
        u = f.lt()
        for g in G:
            if g.lm().divides(u):
                t = u//g.lm()     # We could do u//g.lt() here and not divide by g.lc()
                f -= t*g//g.lc()  # here, but that would only work for polynomials over fields
                break
        else:
            h += u
            f -= u

    return h
