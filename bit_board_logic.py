from bit_board_masks import *
import ctypes

# loading compiled c code
bmi2 = ctypes.CDLL("./bmi2_bitops.so")

bmi2.pext_native.argtypes = [ctypes.c_uint64, ctypes.c_uint64]
bmi2.pext_native.restype = ctypes.c_uint64

bmi2.pdep_native.argtypes = [ctypes.c_uint64, ctypes.c_uint64]
bmi2.pdep_native.restype = ctypes.c_uint64

def pext(source: int, mask: int) -> int:
    """
    Calls the PEXT function from the C library.
    """
    return bmi2.pext_native(source, mask)

def pdep(source: int, mask: int) -> int:
    """
    Calls the PDEP function from the C library.
    """
    return bmi2.pdep_native(source, mask)

# Example usage
source_bitboard = 0b000100000001000000000000011000000010000001000000000100000001000000000010000000001
mask_bitboard =   0b000000000000000000000000011000001010000001100000000000000000000000000000000000000

# Perform PEXT (Extract)
extracted = pext(source_bitboard, mask_bitboard)
print(f"PEXT Result: {bin(extracted)[2:]}")

# Perform PDEP (Deposit)
deposited = pdep(extracted, mask_bitboard)
print(f"PDEP Result: {bin(deposited)[2:].zfill(81)}")