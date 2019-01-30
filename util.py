def to_signed_byte(value):
    if value & 0x80:
        return -((value - 1) ^ 0xFF)
    return value


def to_signed_short(value):
    if value & 0x8000:
        return -((value - 1) ^ 0xFFFF)
    return value


def to_signed_int(value):
    if value & 0x80000000:
        return -((value - 1) ^ 0xFFFFFFFF)
    return value
