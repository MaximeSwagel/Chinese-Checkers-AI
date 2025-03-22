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
    Calls the PEXT function from the C library on a 128 bit source and mask
    by splitting them into two 64 bit parts and recombine results.
    """
    # Lower part is the first 64 bits, high is the next 64 bits
    source_low = source & 0xFFFFFFFFFFFFFFFF
    source_high = (source >> 64) & 0xFFFFFFFFFFFFFFFF

    mask_low = mask & 0xFFFFFFFFFFFFFFFF
    mask_high = (mask >> 64) & 0xFFFFFFFFFFFFFFFF

    # Call pdep for both
    extracted_low = bmi2.pext_native(source_low, mask_low)
    extracted_high = bmi2.pext_native(source_high, mask_high)

    # Counts the amount of 1 in the lower 64 bit mask
    shift_amount = bin(mask_low).count('1')

    # Combine the two by shifting the high part 64 to the left and or the two lines together
    result = extracted_low | (extracted_high << shift_amount)

    return result

def pdep(source: int, mask: int) -> int:
    """
    Calls the PDEP function from the C library.
    """
    # Count the number of 1 bits in the lower mask
    lower_bit_count = bin(mask & 0xFFFFFFFFFFFFFFFF).count("1")

    # divide the source into what belong in the lower section and higher section
    source_low = source & ((1 << lower_bit_count) - 1)
    source_high = source >> lower_bit_count

    # Dividing the mask in two
    mask_low = mask & 0xFFFFFFFFFFFFFFFF
    mask_high = (mask >> 64) & 0xFFFFFFFFFFFFFFFF

    # Call C function for lower and upper parts
    deposited_low = bmi2.pdep_native(source_low, mask_low)
    deposited_high = bmi2.pdep_native(source_high, mask_high)
    
    # Combine the two by shifting the high part 64 to the left and or the two lines together
    result = deposited_low | (deposited_high << 64)

    return result

#Here in the C code you use 64 bits, isn't that too few for our 81 bits long board ?

# # Example usage
# # source_bitboard = 0b100100000001000000000000011000000010000001000000000100000001000000000010000000001
# # mask_bitboard =   0b100100000000000000000000011000001010000001100000000000000000000000000000000000001

# source_bitboard = 0b100100000001000000000000011000000010000001000000000100000001000000000010000000001
# mask_bitboard = 0b100100000001000000000000011000000010000001000000000100000001000000000010000000001

# # Perform PEXT (Extract)
# extracted = pext(source_bitboard, mask_bitboard)
# print(f"PEXT Result: {bin(extracted)[2:]}")

# # Perform PDEP (Deposit)
# deposited = pdep(extracted, mask_bitboard)
# print(f"PDEP Result: {bin(deposited)[2:].zfill(81)}")

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

#########################
# Implementation
#########################

def bit_to_index(bit, width=81):
    """
    Given that index 0 is the rightmost bit (least significant bit),
    return the zero-based index of the single set bit from the right.
    
    Example:
      If bit = 0b100 (decimal 4), bit_length() = 3, so we return 2.
      That means the bit is at index 2 from the right.
    """
    # If bit has exactly one set bit, its position from the right is:
    return bit.bit_length() - 1

def extract_bits(bit_mask):
    """
    For a given bit_mask, return a list of integer masks,
    each containing exactly one bit set from 'bit_mask'.

    Example: if bit_mask = 0b01100 (decimal 12),
    this returns [0b01000, 0b00100].
    (The order is highest bit first, but it's okay for enumerating.)
    """
    pieces = []
    while bit_mask:
        highest_bit_position = bit_mask.bit_length() - 1
        highest_bit = 1 << highest_bit_position
        pieces.append(highest_bit)
        bit_mask ^= highest_bit
    return pieces


#########################
# Move Generation
#########################
# The following assume you have something like:
# neighbors_masks_list
# potential_jumps_list
# and that node_index = 0 => rightmost bit in bitboard, node_index = 80 => leftmost bit

def step_moves(bit_piece, bitboard_occupied):
    # 'bit_piece' is a single-bit integer. We find its index from the right:
    piece_index = bit_to_index(bit_piece)
    # The potential step moves for that index:
    possible_steps_mask = neighbors_masks_list[piece_index]
    # We can only move to empty squares, i.e. not occupied:
    step_move_masks = (~bitboard_occupied) & possible_steps_mask
    return step_move_masks

def intermediate_jump_moves(bit_piece, bitboard_occupied):
    piece_index = bit_to_index(bit_piece)
    # neighbors mask for that piece
    neighbors_mask = jump_over_masks[piece_index]
    # potential jumps mask for that piece
    jumps_mask     = potential_jumps_list[piece_index]
    
    # Use PEXT to see which neighbor bits are occupied and which jump bits are occupied:
    neighbor_compact        = pext(bitboard_occupied, neighbors_mask)
    occupied_jump_compact   = pext(bitboard_occupied, jumps_mask)
    ##
    # print(bin(jumps_mask)[2:].zfill(81))
    # print(f"bit_board_logic/intermediate_jump_moves NEIGHBOUR COMPACT: {bin(neighbor_compact)[2:].zfill(81)}")
    # print(f"bit_board_logic/intermediate_jump_moves JUMPT COMPACT: {bin(occupied_jump_compact)[2:].zfill(81)}")
    # print(f"bit_board_logic/intermediate_jump_moves Exp NEIGBOUR COMPACT: {bin(pdep(neighbor_compact, neighbors_mask))[2:].zfill(81)}")
    # print(f"bit_board_logic/intermediate_jump_moves Exp JUMPT COMPACT: {bin(pdep(occupied_jump_compact, jumps_mask))[2:].zfill(81)}")
    ##
    
    # "neighbor_compact AND NOT occupied_jump_compact"
    # means "the neighbor is occupied but the jump landing is free"
    # that is the 'intermediate' set:
    intermediate_compact = neighbor_compact & (~occupied_jump_compact)

    ##
    # print(f"bit_board_logic/intermediate_jump_moves COMPACT: {bin(intermediate_compact)[2:].zfill(81)}")
    # print(f"bit_board_logic/intermediate_jump_moves exp COMPACT: {bin(pdep(intermediate_compact, jumps_mask))[2:].zfill(81)}")
    ##
    ##
    # print(f"bit_board_logic/intermediate_jump_moves : {bin(intermediate_compact)[2:].zfill(81)}")
    ##
    
    # Now expand it (deposit) back into board space:
    intermediate_jump_move_masks = pdep(intermediate_compact, jumps_mask)
    ##
    # print(f"bit_board_logic/intermediate_jump_moves : {bin(intermediate_jump_move_masks)[2:].zfill(81)}")
    ##
    return intermediate_jump_move_masks

def jump_moves(bit_piece, bitboard_occupied):
    new_moves_found = intermediate_jump_moves(bit_piece, bitboard_occupied)
    new_move_tracker = new_moves_found  # track everything we've found so far

    ##
    # print(f"bit_board_logic/jump_moves : {bin(new_move_tracker)[2:].zfill(81)}")
    ##
    
    while new_moves_found:
        new_move_bits = extract_bits(new_moves_found)
        new_moves_found = 0
        for position_bit in new_move_bits:
            # For each newly found jump position, see if we can jump further
            further_moves = intermediate_jump_moves(position_bit, bitboard_occupied)
            # Exclude moves we've already found
            further_moves &= ~new_move_tracker
            # Accumulate
            new_moves_found |= further_moves
            new_move_tracker |= further_moves
    
    return new_move_tracker

def moves(bit_piece, bitboard_occupied):
    # All possible moves from 'bit_piece' are single-step or jump-based:
    step = step_moves(bit_piece, bitboard_occupied)
    jump = jump_moves(bit_piece, bitboard_occupied)

    ##
    # print(f"bit_board_logic/moves : {bin(bitboard_occupied)[2:].zfill(81)}")
    # print(f"bit_board_logic/moves : {bin(step)[2:].zfill(81)}")
    # print(f"bit_board_logic/moves : {bin(jump)[2:].zfill(81)}") #this is wrong 
    ##
    all_moves = step | jump
    return all_moves


#########################
# Applying a Move
#########################
def play_move(bit_piece, bit_move, bitboard_occupied, bitboard_player):
    """
    Given 'bit_piece' is the single bit representing the piece to move,
    and 'bit_move' is the single bit representing the new location,
    flip both squares in 'bitboard_occupied' and 'bitboard_player' via XOR.
    
    Returns the updated (bitboard_occupied, bitboard_player).
    """
    move_mask = bit_piece | bit_move
    new_bitboard_occupied = bitboard_occupied ^ move_mask
    new_bitboard_player   = bitboard_player   ^ move_mask
    return new_bitboard_occupied, new_bitboard_player
