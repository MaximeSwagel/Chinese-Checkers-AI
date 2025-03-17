import networkx as nx
import matplotlib.pyplot as plt
from bit_board_masks import *
from bit_board_logic import bit_to_index ,extract_bits, moves, play_move

# Here we try to reconcile the bitboard representation with the visualizations. 
# I gave GPT the code that we have done and asked it to make a function that uses our bitboard representation
# to visualize it as we had done initially.
#I asked chat gpt to make it shorter

def visualize_bitboard(occ, p1, p2, hex_layers=9, player_layers=4):
    G = nx.Graph(); pos2i = {}; i2pos = {}  # Maps for fast lookups
    idx = 0; last_row = []

    # Build top (expanding) half
    for r in range(hex_layers):
        row = []
        for q in range(-r, r+1, 2):
            pos2i[(q,r)] = idx; i2pos[idx] = (q,r)
            G.add_node(idx); row.append(idx); idx += 1
        if r > 0:
            for i in range(len(row)):
                if i > 0: G.add_edge(row[i], row[i-1])
                if i < len(last_row): G.add_edge(row[i], last_row[i])
                if i > 0: G.add_edge(row[i], last_row[i-1])
        last_row = row

    buffer_rows = []
    # Build bottom (contracting) half
    for r in range(hex_layers, 2*hex_layers - 1):
        row = []
        for q in range(-(2*hex_layers-r-2), 2*hex_layers-r-1, 2):
            pos2i[(q,r)] = idx; i2pos[idx] = (q,r)
            G.add_node(idx); row.append(idx); idx += 1
        for i, prev in enumerate(last_row):
            qp, rp = i2pos[prev]  # O(1) lookup instead of O(N)
            for dq, dr in ([(1,1)] if i==0 else ([(-1,1)] if i==len(last_row)-1 else [(1,1), (-1,1)])):
                if (qp+dq, rp+dr) in pos2i: G.add_edge(prev, pos2i[(qp+dq, rp+dr)])
        for i in range(len(row)-1): G.add_edge(row[i], row[i+1])
        buffer_rows.append(row)
        if len(buffer_rows) > player_layers: buffer_rows.pop(0)
        last_row = row

    # Prepare visualization
    visual_pos = {i: (q, -r) for i, (q,r) in i2pos.items()}
    p1_nodes, p2_nodes, empty_nodes = [], [], []
    for i in range(idx):
        mask = 1 << i
        if occ & mask: (p1_nodes if p1 & mask else p2_nodes).append(i)
        else: empty_nodes.append(i)

    # Draw board
    plt.figure(figsize=(10,10))
    nx.draw_networkx_edges(G, visual_pos, edge_color="gray")
    nx.draw_networkx_nodes(G, visual_pos, nodelist=empty_nodes, node_color="lightgray", node_size=500)
    nx.draw_networkx_nodes(G, visual_pos, nodelist=p1_nodes, node_color="red", node_size=500)
    nx.draw_networkx_nodes(G, visual_pos, nodelist=p2_nodes, node_color="blue", node_size=500)
    nx.draw_networkx_labels(G, visual_pos, {n: str(n) for n in G.nodes()}, font_size=8)
    plt.title("Bitboard-based Chinese Checkers")
    plt.axis("equal")

"""

from bitboard_masks we have :

    player1_pieces = 0b000000000000000000000000000000000000000000000000000000000000000000000001111111111
    player2_pieces = 0b111111111100000000000000000000000000000000000000000000000000000000000000000000000

    all_pieces = 0b111111111100000000000000000000000000000000000000000000000000000000000001111111111

"""

#Here we copy the code of test_logic just to have a first visualization of making a move:

visualize_bitboard(all_pieces, player1_pieces, player2_pieces)

player1_bit_pieces = extract_bits(player1_pieces)

#Dictionnary of possible moves for each piece of player1 (pieces represented by their binary positions and moves represented by a move mask)
possible_moves_player1 = {bin(bit_piece) : bin(moves(bit_piece,  all_pieces)) for bit_piece in player1_bit_pieces}

#then the list of moves for a selected piece (arbitrarily we take the first one of the dict):
selected_piece = next(iter(possible_moves_player1))
selected_piece_move_mask = int(possible_moves_player1[selected_piece],2)
selected_piece_move_list = extract_bits(selected_piece_move_mask)

#Select one move and apply it (arbitrarily we take the first one of the list)
selected_move = selected_piece_move_list[0]
print(f"Selected piece : {bin(int(selected_piece,2))[2:].zfill(81)}")
print(f"Selected move : {bin(selected_move)[2:].zfill(81)}")

print(bin(all_pieces))
all_pieces, player1_pieces = play_move(int(selected_piece,2), selected_move, all_pieces, player1_pieces)
print(bin(all_pieces))

visualize_bitboard(all_pieces, player1_pieces, player2_pieces)

#It works !!