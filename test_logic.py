from bit_board_logic import bit_to_index ,extract_bits, moves, play_move
from game_board import generate_two_player_chinese_checkers

hex_layers = 9
player_layers = 4

G, node_positions, player1_nodes, player2_nodes = generate_two_player_chinese_checkers(hex_layers, player_layers)

bitboard_mapping = {index: 1 << index for index in node_positions.values()}
# Initialize bitboards
# Player one
# 0b000000000000000000000000000000000000000000000000000000000000000000000001111111111
bitboard_player1 = sum(bitboard_mapping[node] for node in player1_nodes)
# 0b111111111100000000000000000000000000000000000000000000000000000000000000000000000
bitboard_player2 = sum(bitboard_mapping[node] for node in player2_nodes)

#This is how we get the right bit representation for the game, but we store them as normal bits
print(bin(bitboard_player1)[2:].zfill(81))

# Using logical or we can combine they two to get all the pieces
# 0b111111111100000000000000000000000000000000000000000000000000000000000001111111111
bitboard_occupied = bitboard_player1 | bitboard_player2


player1_bit_pieces = extract_bits(bitboard_player1)


#Dictionnary of possible moves for each piece of player1 (pieces represented by their binary positions and moves represented by a move mask)
possible_moves_player1 = {bin(bit_piece) : bin(moves(bit_piece, bitboard_occupied)) for bit_piece in player1_bit_pieces}

#then the list of moves for a selected piece (arbitrarily we take the first one of the dict):

selected_piece = next(iter(possible_moves_player1))
selected_piece_move_mask = int(possible_moves_player1[selected_piece],2)
print(selected_piece_move_mask)
#Convert the mask as a list of moves:

print(type(selected_piece_move_mask), selected_piece_move_mask)
selected_piece_move_list = extract_bits(selected_piece_move_mask)

#Select one move and apply it (arbitrarily we take the first one of the list)

selected_move = selected_piece_move_list[0]
print(f"Selected piece : {bin(int(selected_piece,2))[2:].zfill(81)}")
print(f"Selected move : {bin(selected_move)[2:].zfill(81)}")

print(bin(bitboard_occupied))
bitboard_occupied, bitboard_player1 = play_move(int(selected_piece,2), selected_move, bitboard_occupied, bitboard_player1)
print(bin(bitboard_occupied))

