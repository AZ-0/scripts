def crack_lcg(s: list) -> tuple:
    from math import gcd
    t = [s[i+1] - s[i] for i in range(len(s) -1)]
    u = [abs(t[i+2]*t[i] - t[i+1]**2) for i in range(len(t) -2)]

    # the more values you provide at the start, the higher the probability of finding m is.
    m = gcd(*u)

    a = t[1] * pow(t[0], -1, m) % m
    b = s[1] - a*s[0]

    return m, a, b % m


from math import gcd
from tqdm import trange
from collections import Counter

def crack_lcg_filtered(vals: list, length: int, min: int = None) -> tuple:
    '''
    Crack a filtered LCG, assuming you have at least `length` consecutive values between each rejections.
    If provided, can use the information that `m > min` to get much better results for lower lengths.
    '''
    ms = []
    for i in trange(len(vals) - length):
        try:
            ms.append(crack_lcg(vals[i:i+length]))
        except ValueError:
            pass

    if not min:
        [(m, _)] = Counter(ms).most_common(1)
        return m
    
    gs = []
    for i in trange(len(ms)):
        for j in range(i):
            g = gcd(ms[i][0], ms[j][0])
            if g > min:
                gs.append((g, ms[i][1] % g, ms[i][2] % g))

    [(m, _)] = Counter(gs).most_common(1)
    return m
