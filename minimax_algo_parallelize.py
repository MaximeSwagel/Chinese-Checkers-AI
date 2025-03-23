from concurrent.futures import ProcessPoolExecutor
import math
import multiprocessing

from bit_board_logic import extract_bits, iterate_bits, moves, play_move
from minimax_algo import minimax, search_stats

def minimax_wrapper(args):
    piece, move, bitboard_player, bitboard_opponent, bitboard_occupied, depth = args

    search_stats.clear()

    new_occupied, new_player = play_move(piece, move, bitboard_occupied, bitboard_player)
    score = minimax(new_player, bitboard_opponent, new_occupied, depth - 1, -math.inf, math.inf, False)

    stats_snapshot = dict(search_stats)
    return score, (piece, move), stats_snapshot

def best_move_parallelized(bitboard_player, bitboard_opponent, bitboard_occupied, depth=4):
    best_score = -math.inf
    best_move_choice = None

    total_states = 0
    total_leaves = 0
    total_moves = 0

    all_moves = []
    for piece in iterate_bits(bitboard_player):
        possible_moves = extract_bits(moves(piece, bitboard_occupied))
        # Optional: add move sorting here again
        for move in possible_moves:
            all_moves.append((piece, move, bitboard_player, bitboard_opponent, bitboard_occupied, depth))

    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        results = executor.map(minimax_wrapper, all_moves)

        for score, move_choice, stats in results:
            if score > best_score:
                best_score = score
                best_move_choice = move_choice
            total_states += stats.get("states", 0)
            total_leaves += stats.get("leaf_paths", 0)
            total_moves += stats.get("moves", 0)

    print()
    print("Parallel search stats:")
    print("Total states:", total_states)
    print("Total leaf paths:", total_leaves)
    print("Total moves considered:", total_moves)
    print("Avg branching factor:", round(total_moves / (total_states-total_leaves), 2))

    return best_move_choice

def best_move_hybrid(bitboard_player, bitboard_opponent, bitboard_occupied, depth=4):
    best_score = -math.inf
    best_move_choice = None

    move_scores = quick_serial_search(bitboard_player, bitboard_opponent, bitboard_occupied, depth=2)
    top_moves = get_top_moves(move_scores, 5)

    all_args = [(piece, move, bitboard_player, bitboard_opponent, bitboard_occupied, depth) for _, (piece, move) in top_moves]

    total_states = 0
    total_leaves = 0
    total_moves = 0

    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        results = executor.map(minimax_wrapper, all_args)

        for score, move_choice, stats in results:
            if score > best_score:
                best_score = score
                best_move_choice = move_choice
            total_states += stats.get("states", 0)
            total_leaves += stats.get("leaf_paths", 0)
            total_moves += stats.get("moves", 0)

    print()
    print("\nHybrid search stats:")
    print("Total states:", total_states)
    print("Total leaf paths:", total_leaves)
    print("Total moves considered:", total_moves)
    print("Avg branching factor:", round(total_moves / (total_states-total_leaves), 2))

    return best_move_choice

def get_top_moves(move_scores, top_n=5):
    return sorted(move_scores, reverse=True)[:top_n]

def quick_serial_search(bitboard_player, bitboard_opponent, bitboard_occupied, depth=2):
    move_scores = []
    for piece in iterate_bits(bitboard_player):
        for move in extract_bits(moves(piece, bitboard_occupied)):
            new_occupied, new_player = play_move(piece, move, bitboard_occupied, bitboard_player)
            score = minimax(new_player, bitboard_opponent, new_occupied, depth-1, -math.inf, math.inf, False)
            move_scores.append((score, (piece, move)))
    return move_scores
