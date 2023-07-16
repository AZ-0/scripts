def mult(P, n):
    if n < 0:
        return mult(-P, -n)

    R = 0

    while n:
        if n & 1:
            R += P
        P += P
        n >>= 1
    
    return R