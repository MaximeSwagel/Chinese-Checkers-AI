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


"""
Planned logic

single step moves:
neighbors and not all_pieces


Jump moves:
1. Use pext to extract from all_pieces using neighbors as a mask (calling this neighbor_output)
2. Use pext to extract from all_pieces using potential_jumps as a mask (calling this jump_output)

3. Use logical and for "neighbor_output and not jump_output" (calling this compressed_jumps)

4. Use pdep to spread compressed_jumps using potential_jumps as a mask (calling this final_jump_moves)

Keep a list of the what nodes we visit and repeat for each position in final_jump_moves


To get full list of all moves use logical or on all the outputs



apply moves could be with logical xor

0001010010101001 current board
xor
0101000000000000 steps moved
=
0100010010101001 after moved

"""