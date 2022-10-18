class ProtoDecodeError(Exception):
    pass

def dec_varint(data: bytes) -> int:
    varint = 0
    for i, v in enumerate(data):
        varint |= (v & 0b1111111) << i*7
        if not v >> 7:
            break
    else:
        raise ProtoDecodeError('Truncated varint')

    return data[i+1:], varint

def dec_delim(data: bytes) -> bytes:
    data, len = dec_varint(data)
    return data[len:], data[:len]

def dec_tag(data: bytes) -> tuple[int, int]:
    data, varint = dec_varint(data)
    field = varint >> 3
    wire  = varint & 0b111
    return data, field, wire

def dec_proto(data: bytes) -> dict[int]:
    fields = {}

    while data:
        data, field, wire = dec_tag(data)

        if wire == 0:
            data, fields[field] = dec_varint(data)

        elif wire == 2:
            data, fields[field] = dec_delim(data)

        else:
            raise ProtoDecodeError(f'Unsupported wire type {wire} at field {field}')

    return fields