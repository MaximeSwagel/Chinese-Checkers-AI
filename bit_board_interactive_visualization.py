import cProfile
import time
import networkx as nx
import matplotlib.pyplot as plt
from bit_board_masks import *
from bit_board_logic import bit_to_index ,extract_bits, moves, play_move
from minimax_algo import best_move
from minimax_algo_parallelize import best_move_hybrid, best_move_parallelized

#This was made with the help of chat gpt

def draw_bitboard(ax,
                  occupied_bitboard, 
                  bitboard_player1, 
                  bitboard_player2,
                  hex_layers=9, 
                  player_layers=4,
                  highlight_mask=0):
    """
    Draw the Chinese Checkers board on an existing Axes.
    Optionally highlight the bits in `highlight_mask`.
    """

    # 1) Build the board G, node_positions exactly like your existing logic
    #    (matching the style from `visualize_bitboard`)
    G = nx.Graph()
    pos2i = {}  # (q, r) -> index
    i2pos = {}  # index -> (q, r)
    idx = 0
    last_row = []

    # Top (expanding) half
    for r in range(hex_layers):
        row = []
        for q in range(-r, r+1, 2):
            pos2i[(q, r)] = idx
            i2pos[idx] = (q, r)
            G.add_node(idx)
            row.append(idx)
            idx += 1
        if r > 0:
            for i in range(len(row)):
                if i > 0:
                    G.add_edge(row[i], row[i-1])
                if i < len(last_row):
                    G.add_edge(row[i], last_row[i])
                if i > 0:
                    G.add_edge(row[i], last_row[i-1])
        last_row = row

    # Bottom (contracting) half
    buffer_rows = []
    for r in range(hex_layers, 2*hex_layers - 1):
        row = []
        for q in range(-(2*hex_layers - r - 2),
                       (2*hex_layers - r - 1), 2):
            pos2i[(q, r)] = idx
            i2pos[idx] = (q, r)
            G.add_node(idx)
            row.append(idx)
            idx += 1

        # Connect the new row to the old row
        for i, prev in enumerate(last_row):
            qp, rp = i2pos[prev]
            # Decide which diagonals to link depending on whether
            # it's the leftmost, rightmost, or middle pieces
            if i == 0:
                # connect to (qp+1, rp+1) if it exists
                if (qp+1, rp+1) in pos2i:
                    G.add_edge(prev, pos2i[(qp+1, rp+1)])
            elif i == len(last_row) - 1:
                # connect to (qp-1, rp+1) if it exists
                if (qp-1, rp+1) in pos2i:
                    G.add_edge(prev, pos2i[(qp-1, rp+1)])
            else:
                # connect to both diagonals if they exist
                if (qp+1, rp+1) in pos2i:
                    G.add_edge(prev, pos2i[(qp+1, rp+1)])
                if (qp-1, rp+1) in pos2i:
                    G.add_edge(prev, pos2i[(qp-1, rp+1)])

        # Connect adjacent nodes within the new row
        for i2 in range(len(row) - 1):
            G.add_edge(row[i2], row[i2 + 1])

        buffer_rows.append(row)
        if len(buffer_rows) > player_layers:
            buffer_rows.pop(0)
        last_row = row

    # 2) Convert (q,r) => (x,y) for plotting
    visual_positions = {i: (q, -r) for i, (q, r) in i2pos.items()}

    # --------------------------------------------------------------------
    # The rest of the function (clearing the Axes, drawing edges/nodes,
    # labeling, highlighting, etc.) remains essentially the same.
    # --------------------------------------------------------------------

    ax.clear()
    ax.set_aspect('equal')
    ax.axis("off")
    nx.draw_networkx_edges(G, visual_positions, ax=ax, edge_color="gray")

    # Figure out which nodes are empty / p1 / p2
    player1_nodes = []
    player2_nodes = []
    unoccupied_nodes = []
    for i, (q, r) in i2pos.items():
        bit_mask = 1 << i
        if (occupied_bitboard & bit_mask) != 0:
            if (bitboard_player1 & bit_mask) != 0:
                player1_nodes.append(i)
            elif (bitboard_player2 & bit_mask) != 0:
                player2_nodes.append(i)
            else:
                pass  # If more players exist, handle them here
        else:
            unoccupied_nodes.append(i)

    # Draw them
    nx.draw_networkx_nodes(G, visual_positions, ax=ax,
                           nodelist=unoccupied_nodes,
                           node_color="lightgray",
                           node_size=500)
    nx.draw_networkx_nodes(G, visual_positions, ax=ax,
                           nodelist=player1_nodes,
                           node_color="red",
                           node_size=500)
    nx.draw_networkx_nodes(G, visual_positions, ax=ax,
                           nodelist=player2_nodes,
                           node_color="blue",
                           node_size=500)

    # Draw labels
    label_dict = {n: str(n) for n in G.nodes()}
    nx.draw_networkx_labels(G, visual_positions, label_dict, font_size=8, ax=ax)

    # Highlight possible moves if highlight_mask != 0
    if highlight_mask:
        highlight_nodes = []
        for i in range(len(i2pos)):
            if (highlight_mask & (1 << i)) != 0:
                highlight_nodes.append(i)
        highlight_x = []
        highlight_y = []
        for hi_node in highlight_nodes:
            qh, rh = i2pos[hi_node]
            highlight_x.append(qh)
            highlight_y.append(-rh)

        ax.scatter(highlight_x,
                   highlight_y,
                   s=800,
                   facecolors="none",
                   edgecolors="yellow",
                   linewidths=2,
                   alpha=0.8)
    # (No return; just finish drawing on ax)

def interactive_game(occupied_bitboard, bitboard_player1, bitboard_player2, 
                     hex_layers=9, player_layers=4, ai_player=2):
    """
    Runs an interactive game where the user plays against the AI.
    - Player1 (Red) is human
    - Player2 (Blue) is AI (if ai_player==2)

    This is an infinite loop until you close the figure or interrupt.
    """
    
    # We'll store the current game state in a dictionary
    game_state = {
        "occupied": occupied_bitboard,
        "p1": bitboard_player1,
        "p2": bitboard_player2,
        "turn": 1,  # 1 => Player1 (human), 2 => Player2 (AI)
        "selected_piece_mask": 0,
        "possible_moves_mask": 0
    }

    # Create a figure and axes
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title("Interactive Chinese Checkers (Click-based)")

    # 1) We define a function that re-draws the board
    def redraw():
        # Whose turn is it?
        if game_state["turn"] == 1:
            turn_name = "Player 1 (RED)"
        else:
            turn_name = "Player 2 (BLUE - AI)"
        ax.set_title(f"{turn_name}'s turn.")

        # Use our new draw_bitboard function
        # ##
        # print(f"interactive_visualization/redraw : {bin(game_state['possible_moves_mask'])[2:].zfill(81)}") #this is wrong
        # ##
        highlight = game_state["possible_moves_mask"] # squares to highlight
        draw_bitboard(ax,
                      game_state["occupied"],
                      game_state["p1"],
                      game_state["p2"],
                      hex_layers=hex_layers,
                      player_layers=player_layers,
                      highlight_mask=highlight)

        fig.canvas.draw_idle()

    # 2) The callback for when the user clicks on the board
    def on_click(event):
        if game_state["turn"] == ai_player:
            return  # Ignore clicks if AI is playing

        # If user clicks outside our axes, ignore
        if event.inaxes != ax:
            return

        # We need to figure out which node was clicked
        # Because we re-build the board each time in draw_bitboard, let's do the same
        # node layout. We'll do a quick "find nearest node" approach:
        #   (1) Rebuild the positions from draw_bitboard logic (the quick version).
        #   (2) Compute distance to each node in (x, y) space.

        # Quick re-gen of node_positions:
        node_positions = {}
        node_index = 0
        for r in range(hex_layers):
            for q in range(-r, r+1, 2):
                node_positions[(q, r)] = node_index
                node_index += 1
        for r in range(hex_layers, 2*hex_layers-1):
            q_start = -(2*hex_layers - r - 2)
            q_end   = -q_start
            for q in range(q_start, q_end+1, 2):
                node_positions[(q, r)] = node_index
                node_index += 1

        # We'll invert that dict: index -> (q, r)
        index_to_qr = {v: k for k, v in node_positions.items()}

        # (x, y) from the click
        click_x = event.xdata
        click_y = event.ydata

        # Find the node with minimal distance
        min_dist = float("inf")
        clicked_node = None

        for i in range(len(index_to_qr)):
            (q, r) = index_to_qr[i]
            # remember we draw at (q, -r)
            nx = q
            ny = -r
            dist_sq = (nx - click_x)**2 + (ny - click_y)**2
            if dist_sq < min_dist:
                min_dist = dist_sq
                clicked_node = i

        # Now interpret the click based on game state
        if clicked_node is None:
            return  # no node found

        # Current player
        if game_state["turn"] == 1:
            current_bb = game_state["p1"]
        else:
            current_bb = game_state["p2"]

        mask_for_clicked = (1 << clicked_node)

        # CASE A) No piece selected yet => maybe the user is trying to select a piece
        if game_state["selected_piece_mask"] == 0:
            # Check if it belongs to the current player's bitboard
            if (current_bb & mask_for_clicked) != 0:
                # It's one of your pieces => select it
                game_state["selected_piece_mask"] = mask_for_clicked

                # Compute possible moves

                # ##
                # print(f"interactive_visualization/CASE_A : {bin(game_state['occupied'])[2:].zfill(81)}") #this is good
                # print(f"interactive_visualization/CASE_A : {bin(mask_for_clicked)[2:].zfill(81)}")
                # print(f"interactive_visualization/CASE_A : {bit_to_index(mask_for_clicked)}")
                # ##
                all_moves_mask = moves(mask_for_clicked, game_state["occupied"])
                # ##
                # print(f"interactive_visualization/CASE_A : {bin(all_moves_mask)[2:].zfill(81)}") #this is wrong
                # ##

                game_state["possible_moves_mask"] = all_moves_mask
                redraw()
            else:
                # They clicked something else => do nothing
                return

        # CASE B) We already have a piece selected
        else:
            # Check if the clicked node is a valid move
            if (game_state["possible_moves_mask"] & mask_for_clicked) != 0:
                # => perform the move
                from_piece_mask = game_state["selected_piece_mask"]
                to_piece_mask   = mask_for_clicked

                new_occupied, new_current_bb = play_move(from_piece_mask,
                                                         to_piece_mask,
                                                         game_state["occupied"],
                                                         current_bb)

                # Save changes
                game_state["occupied"] = new_occupied
                if game_state["turn"] == 1:
                    game_state["p1"] = new_current_bb
                else:
                    game_state["p2"] = new_current_bb

                # Clear selection
                game_state["selected_piece_mask"] = 0
                game_state["possible_moves_mask"] = 0

                # Switch turn
                game_state["turn"] = 2 if game_state["turn"] == 1 else 1

                redraw()

                if game_state["turn"] == ai_player:
                    plt.pause(1)
                    ai_turn()

                
            else:
                # Maybe they clicked a different piece of theirs to re-select
                if (current_bb & mask_for_clicked) != 0:
                    game_state["selected_piece_mask"] = mask_for_clicked
                    game_state["possible_moves_mask"] = moves(mask_for_clicked,
                                                              game_state["occupied"])
                    redraw()
                else:
                    # Otherwise, ignore
                    pass
    
    def ai_turn():
        # cProfile.runctx(
        #     "best_move(game_state['p2'], game_state['p1'], game_state['occupied'], depth=4)",
        #     globals(),
        #     locals()
        # )
        
        start = time.perf_counter()
        # ai_move = best_move(game_state["p2"], game_state["p1"], game_state["occupied"], depth=4)
        # ai_move = best_move_parallelized(game_state["p2"], game_state["p1"], game_state["occupied"], depth=4)
        ai_move = best_move_hybrid(game_state["p2"], game_state["p1"], game_state["occupied"], depth=4)
        end = time.perf_counter()
        print(f"AI move took {end - start:.3f} seconds")
        if ai_move:
            from_piece_mask, to_piece_mask = ai_move
            game_state["occupied"], game_state["p2"] = play_move(from_piece_mask, to_piece_mask, game_state["occupied"], game_state["p2"])
        game_state["turn"] = 1
        redraw()

    # 3) Connect the callback
    cid = fig.canvas.mpl_connect("button_press_event", on_click)

    # 4) Initial draw
    redraw()

    # 5) Show and remain interactive
    plt.show(block=True)

    # This function loops forever until the figure is closed or kernel interrupted.

if __name__ == "__main__":
    interactive_game(all_pieces, player1_pieces, player2_pieces,
                     hex_layers=9, player_layers=4)
