def to_bytes(x: int, endian='big', signed=False) -> int:
    return x.to_bytes((x.bit_length() + 7) // 8, endian, signed=signed)

def der_encode_len(ln: int) -> bytes:
    if ln < 0x80:
        return bytes([ln])

    ln = to_bytes(ln)
    return bytes([len(ln) | 0x80]) + ln

def der_encode_int(val: int) -> bytes:
    val = to_bytes(val, signed=True)
    return bytes([2]) + der_encode_len(len(val)) + val

def der_encode(*vals: int):
    body = bytearray()

    for val in vals:
        body.extend(der_encode_int(val))

    return bytes([48]) + der_encode_len(len(body)) + body