from Crypto.Util.number import getPrime, isPrime

def gen_smoothprime(bits, smoothness):
    q, = fs = [2]
    while q.bit_length() < bits - 2 * smoothness:
        fs.append(f := getPrime(smoothness))
        q *= f

    fill = (bits - q.bit_length()) // 2

    p = 0
    while not isPrime(p + 1):
        r, s = getPrime(fill), getPrime(fill)
        p = q * r * s
        
        fill += p.bit_length() < bits
        fill -= p.bit_length() > bits

    fs.extend([r, s])
    fs.sort()
    return p + 1, fs
