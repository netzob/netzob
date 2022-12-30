# xorshift.pyx

from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t

def native_xorshift8(uint8_t state):
    state ^= (state << 7)
    state ^= (state >> 5)
    state ^= (state << 3)
    return state


def native_xorshift16(uint16_t state):
    state ^= (state << 13)
    state ^= (state >> 9)
    state ^= (state << 7)
    return state


def native_xorshift32(uint32_t state):
    state ^= (state << 13)
    state ^= (state >> 17)
    state ^= (state << 5)
    return state


def native_xorshift64(uint64_t state):
    state ^= (state << 11)
    state ^= (state >> 5)
    state ^= (state << 32)
    return state
