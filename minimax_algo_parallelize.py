from concurrent.futures import ProcessPoolExecutor
import math
import multiprocessing

from bit_board_logic import extract_bits, iterate_bits, moves, play_move
from minimax_algo import minimax

def minimax_wrapper(args):
    piece, move, bitboard_player, bitboard_opponent, bitboard_occupied, depth = args
    new_occupied, new_player = play_move(piece, move, bitboard_occupied, bitboard_player)
    score = minimax(new_player, bitboard_opponent, new_occupied, depth - 1, -math.inf, math.inf, False)
    return score, (piece, move)

def best_move_parallelized(bitboard_player, bitboard_opponent, bitboard_occupied, depth=4):
    best_score = -math.inf
    best_move_choice = None

    all_moves = []
    for piece in iterate_bits(bitboard_player):
        possible_moves = extract_bits(moves(piece, bitboard_occupied))
        # Optional: add move sorting here again
        for move in possible_moves:
            all_moves.append((piece, move, bitboard_player, bitboard_opponent, bitboard_occupied, depth))

    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        results = executor.map(minimax_wrapper, all_moves)

        for score, move_choice in results:
            if score > best_score:
                best_score = score
                best_move_choice = move_choice

    return best_move_choice