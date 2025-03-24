from bit_board_masks import *
from bit_board_interactive_visualization import interactive_game

if __name__ == "__main__":
    interactive_game(all_pieces, player1_pieces, player2_pieces, hex_layers=9, player_layers=4)