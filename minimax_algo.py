import math
from bit_board_logic import iterate_bits, moves, play_move, extract_bits, bit_to_index
from functools import lru_cache

from bit_board_masks import ROW_MASKS

pos2ix = {(0, 0): 0, (-1, 1): 1, (1, 1): 2, (-2, 2): 3, (0, 2): 4, (2, 2): 5, (-3, 3): 6,
(-1, 3): 7, (1, 3): 8, (3, 3): 9, (-4, 4): 10, (-2, 4): 11, (0, 4): 12, (2, 4): 13, (4, 4): 14,
(-5, 5): 15, (-3, 5): 16, (-1, 5): 17, (1, 5): 18, (3, 5): 19, (5, 5): 20, (-6, 6): 21, (-4, 6): 22,
(-2, 6): 23, (0, 6): 24, (2, 6): 25, (4, 6): 26, (6, 6): 27, (-7, 7): 28, (-5, 7): 29, (-3, 7): 30,
(-1, 7): 31, (1, 7): 32, (3, 7): 33, (5, 7): 34, (7, 7): 35, (-8, 8): 36, (-6, 8): 37, (-4, 8): 38,
(-2, 8): 39, (0, 8): 40, (2, 8): 41, (4, 8): 42, (6, 8): 43, (8, 8): 44, (-7, 9): 45, (-5, 9): 46,
(-3, 9): 47, (-1, 9): 48, (1, 9): 49, (3, 9): 50, (5, 9): 51, (7, 9): 52, (-6, 10): 53, (-4, 10): 54,
(-2, 10): 55, (0, 10): 56, (2, 10): 57, (4, 10): 58, (6, 10): 59, (-5, 11): 60, (-3, 11): 61, (-1, 11): 62,
(1, 11): 63, (3, 11): 64, (5, 11): 65, (-4, 12): 66, (-2, 12): 67, (0, 12): 68, (2, 12): 69, (4, 12): 70,
(-3, 13): 71, (-1, 13): 72, (1, 13): 73, (3, 13): 74, (-2, 14): 75, (0, 14): 76, (2, 14): 77,
(-1, 15): 78, (1, 15): 79, (0, 16): 80}

ix2pos = {val:key for key,val in pos2ix.items()}

@lru_cache(maxsize=100000)
def evaluate_board(bitboard_player, bitboard_opponent):
    """
    Heuristic function to evaluate board position.
    We evaluate the board by calculating the "mean position" of all pawns of each player.
    This is done by summing the value of each pawns' row and dividing by the total number
    of pawns (10). The player with the higher mean score is considered to be in a winning
    position. 
    """
    bits_player = extract_bits(bitboard_player)
    bits_opponent = extract_bits(bitboard_opponent)
    indexes_player = []
    indexes_opponent = []

    forward_bonus = 5  # Encourages forward movement
    backward_penalty = -3  # Discourages going backward
    multi_jump_bonus = 5  # Reward for jumping multiple times in a row

    total_score = 0

    for bit in bits_opponent:
        index = bit_to_index(bit)
        row = 16-ix2pos[index][1]

        # Reward forward movement
        total_score += row * forward_bonus  

        # Penalize backward movement
        if row < 8:  # Assuming goal is reaching row 16
            total_score += backward_penalty

        if row > 8:  # Assuming goal is reaching row 16
            total_score += multi_jump_bonus * row        

    # for bit in bits_opponent:
    #     indexes_opponent.append(bit_to_index(bit))
    # for bit in bits_player:
    #     indexes_player.append(bit_to_index(bit))

    indexes_player = get_indexes(bitboard_player)
    indexes_opponent = get_indexes(bitboard_opponent)
    
    mean_row_player = 0
    mean_row_opponent = 0

    # for key,val in ix2pos.items():
    #     for index in indexes_player:
    #         if key == index:
    #             mean_row_player+=val[1]
    #     for index in indexes_opponent:
    #         if key == index:
    #             mean_row_opponent+=16-val[1]
    
    # mean_row_player = mean_row_player/10
    # mean_row_opponent = mean_row_opponent/10

    mean_row_player = sum(ix2pos[i][1] for i in indexes_player) / 10
    mean_row_opponent = sum(16 - ix2pos[i][1] for i in indexes_opponent) / 10

    return total_score + mean_row_opponent - mean_row_player # Higher score is better

@lru_cache(maxsize=100000)
def evaluate_board_bit_board(bitboard_player, bitboard_opponent):

    def bit_count(x): return bin(x).count("1")

    GOAL_ROW_TOP = {0, 1, 2}
    GOAL_ROW_BOTTOM = {14, 15, 16}

    player_score = 0
    opponent_score = 0

    for row in range(17):
        mask = ROW_MASKS[row]
        player_bits = bitboard_player & mask
        opponent_bits = bitboard_opponent & mask

        player_count = bit_count(player_bits)
        opponent_count = bit_count(opponent_bits)

        if row in GOAL_ROW_TOP:
            player_score += player_count * 50
        else:
            player_score += player_count * (16 - row)

        if row in GOAL_ROW_BOTTOM:
            opponent_score += opponent_count * 50
        else:
            opponent_score += opponent_count * row

    return player_score - opponent_score

def get_indexes(bitboard):
    return [bit_to_index(b) for b in extract_bits(bitboard)]

def minimax(bitboard_player, bitboard_opponent, bitboard_occupied, depth, alpha, beta, is_maximizing):
    """
    Minimax algorithm with Alpha-Beta Pruning.
    """
    if depth == 0:
        # print("board evaluation : ", evaluate_board(bitboard_player, bitboard_opponent))
        return evaluate_board_bit_board(bitboard_player, bitboard_opponent)
    
    all_pieces = extract_bits(bitboard_player) if is_maximizing else extract_bits(bitboard_opponent)
    
    if is_maximizing:
        best_score = -math.inf
        for piece in all_pieces:
            # possible_moves = moves(piece, bitboard_occupied)
            # move_bits = extract_bits(possible_moves)
            for move in iterate_bits(moves(piece, bitboard_occupied)):
                new_occupied, new_player = play_move(piece, move, bitboard_occupied, bitboard_player)
                score = minimax(new_player, bitboard_opponent, new_occupied, depth - 1, alpha, beta, False)
                best_score = max(best_score, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break  # Prune the branch
        return best_score
    else:
        best_score = math.inf
        for piece in all_pieces:
            # possible_moves = moves(piece, bitboard_occupied)
            # move_bits = extract_bits(possible_moves)
            for move in iterate_bits(moves(piece, bitboard_occupied)):
                new_occupied, new_opponent = play_move(piece, move, bitboard_occupied, bitboard_opponent)
                score = minimax(bitboard_player, new_opponent, new_occupied, depth - 1, alpha, beta, True)
                best_score = min(best_score, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break  # Prune the branch
        return best_score

def best_move(bitboard_player, bitboard_opponent, bitboard_occupied, depth=4):
    """
    Find the best move for the AI using Minimax with Alpha-Beta Pruning.
    """
    best_score = -math.inf
    best_move_choice = None
    alpha, beta = -math.inf, math.inf
    
    for piece in iterate_bits(bitboard_player):
        # possible_moves = moves(piece, bitboard_occupied)
        # move_bits = extract_bits(possible_moves)

        # # Sort moves: prioritize forward moves first
        # move_bits.sort(key=lambda move: ix2pos[bit_to_index(move)][1] - ix2pos[bit_to_index(piece)][1], reverse=True)

        for move in iterate_bits(moves(piece, bitboard_occupied)):
            new_occupied, new_player = play_move(piece, move, bitboard_occupied, bitboard_player)
            score = minimax(new_player, bitboard_opponent, new_occupied, depth - 1, alpha, beta, False)
            if score > best_score:
                best_score = score
                best_move_choice = (piece, move)
            alpha = max(alpha, score)
            if beta <= alpha:
                break  # Prune the branch
    
    return best_move_choice