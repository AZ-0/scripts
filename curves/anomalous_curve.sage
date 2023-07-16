# Author: Genni

import random
from Crypto.Util.number import isPrime

def gen_anomalous_curve_with_smooth_p(smoothness):
    P = Primes()
    primes = [P.unrank(x) for x in range(10000)]

    """
    4*p = 1 + D*y^2
    let p = p1*p2*p3*...*pn + 1
    4*(p1*p2*...*pn + 1) = 1 + D*y^2
    4*p1*p2*...*pn = D*y^2 - 3

    #4*p1*... = 0 mod 4 = D*y^2 - 3
    #D*y^2 = 3 mod 4, so D = 3 mod 4, and y = 1 mod 4 or y = 3 mod 4 
    """

    D = 11

    dp = dict()

    for trial in range(1000000):
        pns = [8]
        ys = [int(mod(3 * inverse_mod(D, 8), 8).sqrt())]

        """
        y = sqrt(3/D) mod 8, so that (D*y^2 - 3) = 0 % 8 and so that (D*y^2 - 3) // 4 = 0 mod 2,
        so that (D*y^2 - 3) // 4 + 1 is odd, hence making it so that p has an actual chance of being prime
        """
        
        fault = 0
        while(1):
            pn = random.choice(primes)
            if pn == D:
                fault = 1
                break
            targ = 3 * pow(D, -1, pn)

            if kronecker(targ, pn) == 1 and pn not in pns:
                if pn in dp:
                    ypart = dp[pn]
                else:
                    ypart = mod(targ, pn).sqrt()
                    dp[pn] = ypart
                pns.append(int(pn))
                ys.append(int(ypart))

            if prod(pns) > 2**130:
                break

        if fault:
            continue

        y = CRT(ys, pns)
        lhs = D*y^2 - 3
        p1kn = int(lhs/4)
        fac = list(factor(p1kn))
        p = p1kn + 1

        if isPrime(p) and max([x[0] for x in fac]) < smoothness:
            print("found candidate")
            Fp = GF(p)
            Hd = hilbert_class_polynomial(-D)
            R.<x> = Fp[]
            j = R(Hd).roots()[0][0]
            a = -Fp(3*j)/(j-1728)
            b = Fp(2*j)/(j-1728)

            E = EllipticCurve(Fp, [a, b])
            if E.order() == p:
                print(f"{p = }")
                print(f"{a = }")
                print(f"{b = }")