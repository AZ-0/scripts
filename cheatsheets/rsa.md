# RSA

## Implementations
https://github.com/jvdsn/crypto-attacks

## Key Recovery
https://hal.archives-ouvertes.fr/hal-03045663/document

## Coppersmith
https://github.com/defund/coppersmith
https://github.com/mimoo/RSA-and-LLL-attacks/
https://link.springer.com/chapter/10.1007/978-3-540-24676-3_29


- `X`: bound
- `β`: solve modulo `b ≥ N^β` where `b | N`
- `δ`: degree

```hs
    X = 1/2 N^{β²/δ - ε}
<=> ε = β²/δ - log(2*X)/log(N)
```