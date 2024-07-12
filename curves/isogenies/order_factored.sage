def _mult(x, q, r):
    """Compute x*q**r iteratively"""
    for _ in range(r):
        x *= q
    return x


def order_factored(P, n, facs, mult=_mult):
    """
    Let `o` the order of `P`.
    Assuming `o|n` and all prime factors of `o` are in `facs`, find `o`.
    Complexity is bounded by `O(|facs| * log n * log log n)` calls to `mult`.

    INPUT:

    * "P" -- group element (assumed abelian for convenience's sake)

    * "n" -- integer: multiple of the order of `P`

    * "facs" -- list of primes: contains at least the prime factors of the order of `P`

    * "mult" (optional) -- a function `mult(P,q,r)` that returns `(q**r)P`  (default: compute iteratively)

    OUTPUT:

    The order of `P`.
    """

    o = 1
    for q in facs:
        v = n.valuation(q)
        Q = (n//q**v)*P

        l,h = 0,v
        while h > l+1:
            mid = (h+l)//2
            if mult(Q, q, mid).is_zero():
                h = mid
            else:
                l = mid

        if l < h and mult(Q, q, l).is_zero():
            h = l
        o *= q**h

    return o