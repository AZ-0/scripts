p  = 127
Px = 45
F = GF(p)
R.<A> = F[]
E = EllipticCurve(F, [0, 1, 0, 1, 0], check=False)
E._EllipticCurve_generic__ainvs = (0, A, 0, 1, 0)
E.b_invariants.clear_cache()
E.division_polynomial(3, x=Px).roots()
# [(102949529479512543890580884241681214159025774728325125909236782065003257130559, 1)]
