########################### CHALL ###########################
nbits = 64
p = random_prime(2^nbits)
d = 5

n = d//2 + 1
B = 2^(nbits // (d + 1))

K.<X> = GF(p)[]
f = K([randint(-B, B) for _ in range(d+1)])

xs = [randint(0, p-1) for _ in range(n)]
ys = [f(x) for x in xs]

print('f =', f)

########################### SOLVE ###########################
nvars = d + 1 - n # d: degree of polynomial, n: amount of given points

F = PolynomialRing(GF(p), names=','.join(f'y{i}' for i in range(nvars)))
K.<X> = F.fraction_field()[]

points = [*zip(xs, ys)] + [*enumerate(F.gens())]
Q = K.lagrange_polynomial(points)
Q = K([1 * c for c in Q.list()]) # force evaluation of denominators, otherwise it can be stuck on things like a*y/a for some reason
print('Q =', Q)

coeffs = []
for g in F.gens() + (F(1),):
    coeffs.append([F(c).monomial_coefficient(g).lift() for c in Q.list()])
print('coeffs =', coeffs)

M = matrix(ZZ, coeffs)
I = identity_matrix(ZZ, M.nrows())
P = identity_matrix(ZZ, M.ncols()) * p
Z = zero_matrix(ZZ, P.nrows(), I.ncols())
N = vector(ZZ, [0]*(P.nrows() + M.nrows() - 1) + [1 << 3*nbits])

print('Running LLL...')
B = Z.stack(I).augment(P.stack(M)).augment(N)
L = B.LLL()

for v in L:
    if v[I.ncols() - 1] == 1:
        print('v =', v)
        break
else:
    print('Something went wrong!')
    print(L.str())

points[-nvars:] = enumerate(v[:nvars])
f = GF(p)['X'].lagrange_polynomial(points)
print('f =', f)