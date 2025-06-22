from sage.all import *

import numpy as np
from collections import defaultdict
from time import time

proof.all(False)



def eigenvectors_in_extension_field(M, d, K = None):
    """
    Given a square matrix M over Fp, finds (right) eigenvectors in K = Fp^d.

    Output format: a dictionary of the form { eigenvalue : [ eigenvectors ] }
    """
    f = M.minimal_polynomial()
    f_ = f.factor()

    fs = defaultdict(list)
    for g, e in f_:
        d_ = g.degree()
        if d % d_ == 0:
            fs[d_].append((g,e))
    print('fs =', fs)


    if K is None:
        K = GF((p,d), names=f'z{d}', proof=False)

    vs = {}
    for d_, gs in fs.items():
        K_ = K.subfield(d_)
        M_ = M.change_ring(K_)
        φ  = K_.frobenius_endomorphism()

        durations = []

        for i, (g, e) in enumerate(gs):
            time_before = time()

            print('=====> e =', e, '; g =', g)
            r = g.any_root(K_)
            print('---> r =', r)
            _, Ker = (M_ - r)._right_kernel_matrix_over_field()
            vs[K(r)] = Ker.change_ring(K).rows()

            for _ in range(d_ - 1):
                r = φ(r)
                print('---> r =', r)
                Ker = Ker.apply_morphism(φ)
                vs[K(r)] = Ker.change_ring(K).rows()

            elapsed = time() - time_before
            durations.append(elapsed)
            print(f'Searching degree {d_} eigenvectors. ETA: {np.mean(durations) * (len(gs) - i - 1):0.3f} seconds remaining')
        print('Found them all!')


# Find eigenvectors in Fp^4
p = next_prime(401)
d = 4

k = GF(p)
M = matrix.random(k, p, p)
print('Generated matrix!')

eigenvectors_in_extension_field(M, d)