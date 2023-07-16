def extension_degree(L):
    if hasattr(L, 'degree'):
        return L.degree()

    if hasattr(L, 'rank'):
        return L.rank()

    if hasattr(L, 'dimension'):
        return L.dimension()

    raise AttributeError(f"Couldn't determine extension degree of {L}")


# This one gives the polynomial with maximal degree

def as_poly_of(self, gen, d=None, name='x'):
    """Expresses `self` as a polynomial of degree `d` in `gen`"""
    L = parent(self)
    if d is None:
        d = extension_degree(L)

    vecs = [vector(self)] + [vector(gen^i) for i in range(d + 1)]
    dependence = parent(vecs[0]).linear_dependence(vecs)

    coeffs = next((list(coeffs) for coeffs in dependence if coeffs[0].is_unit()), None)
    if coeffs is None:
        raise ArithmeticError(f'Cannot express {self} as a polynomial of degree {d} in {gen}. Try raising the degree!')

    return L.base_ring()[name](coeffs[1:])/-coeffs[0]


# This one gives the polynomial with minimal degree

def as_poly_of2(self, gen, d=None, name='x'):
    """Expresses `self` as a polynomial of degree at most `d` in `gen`"""
    L = parent(self)
    if d is None:
        d = extension_degree(L)

    vecs = [vector(gen^i) for i in range(d + 1)]
    vecs = [vecs[i] for i in matrix(vecs).pivot_rows()]

    try:
        coeffs = parent(vecs[0]).subspace_with_basis(vecs).coordinate_vector(vector(self))
    except ArithmeticError:
        raise ArithmeticError(f'Cannot express {self} as a polynomial of degree {d} in {gen}. Try raising the degree!')

    return L.base_ring()[name](list(coeffs))