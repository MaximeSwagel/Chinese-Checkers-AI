import networkx as nx
import matplotlib.pyplot as plt


"""
Why spend 20 min manually making the board, when you can spend 5 hours trying to generate the board


(q, r)

Left        -> (q+2, r)
Right       -> (q-2, r)  #I think here left and right are inversed
Up-left     -> (q-1, r-1)
Up-right    -> (q+1, r-1)
Down-left   -> (q-1, r+1)
Down-right  -> (q+1, r+1)
"""


def generate_two_player_chinese_checkers(layers, player_layers):
    G = nx.Graph()
    node_positions = {}
    node_index = 0

    player1_nodes = []
    player2_nodes = []

    last_layer_nodes = []

    # Expanding phase
    for r in range(layers):
        row_nodes = []

        for q in range(-r, r + 1, 2):
            node_positions[(q, r)] = node_index
            G.add_node(node_index, pos=(q, r))
            row_nodes.append(node_index)
            if r < player_layers: # Add the first layers to player 1 starting positions
                player1_nodes.append(node_index)
            node_index += 1

        # Connect to the previous layer
        if r > 0:
            prev_layer_nodes = last_layer_nodes

            for i in range(len(row_nodes)):
                # Connect horizontally
                if i > 0:
                    G.add_edge(row_nodes[i], row_nodes[i - 1])
                # Down-left connection
                if i < len(prev_layer_nodes):
                    G.add_edge(row_nodes[i], prev_layer_nodes[i])
                # Down-right connection
                if i > 0:
                    G.add_edge(row_nodes[i], prev_layer_nodes[i - 1])

        # Store last layer for contraction phase
        last_layer_nodes = row_nodes

    last_layers_buffer = [] # Overcomplicated way of remembering the last layers for adding them to player 2

    # Contracting phase
    for r in range(layers, 2 * layers - 1):
        row_nodes = []
        q_start = -(2 * layers - r - 2)
        q_end = -q_start

        for q in range(q_start, q_end + 1, 2):
            node_positions[(q, r)] = node_index
            G.add_node(node_index, pos=(q, r))
            row_nodes.append(node_index)
            node_index += 1

        prev_layer_nodes = last_layer_nodes

        for i in range(len(prev_layer_nodes)):
            q, r_prev = [key for key, value in node_positions.items() if value == prev_layer_nodes[i]][0]

            if i == 0:
                # Left most node only connects down-right
                down_right_pos = (q + 1, r_prev + 1)
                if down_right_pos in node_positions:
                    G.add_edge(prev_layer_nodes[i], node_positions[down_right_pos])
            elif i == len(prev_layer_nodes) - 1:
                # Right most node only connects down-left
                down_left_pos = (q - 1, r_prev + 1)
                if down_left_pos in node_positions:
                    G.add_edge(prev_layer_nodes[i], node_positions[down_left_pos])
            else:
                # Middle nodes connect to both corresponding positions above
                down_right_pos = (q + 1, r_prev + 1)
                down_left_pos = (q - 1, r_prev + 1)
                if down_right_pos in node_positions:
                    G.add_edge(prev_layer_nodes[i], node_positions[down_right_pos])
                if down_left_pos in node_positions:
                    G.add_edge(prev_layer_nodes[i], node_positions[down_left_pos])

        for i in range(len(row_nodes) - 1):
            G.add_edge(row_nodes[i], row_nodes[i + 1])
        last_layers_buffer.append(row_nodes)

        if len(last_layers_buffer) > player_layers: # Keep only the last {player_layers} amount of layers in the buffer
            last_layers_buffer.pop(0)

        last_layer_nodes = row_nodes

    # Flatten the buffer and add to list of player 2 starting layers
    player2_nodes = [node for layer in last_layers_buffer for node in layer]

    return G, node_positions, player1_nodes, player2_nodes


hex_layers = 9 # Amount of layers from top of player 1 to middle of the board
player_layers = 4 # Number of layers the players start in
G, node_positions, player1_nodes, player2_nodes = generate_two_player_chinese_checkers(hex_layers, player_layers)



# Everything below is for visualising

visual_positions = {node: (q, -r) for (q, r), node in node_positions.items()}

plt.figure(figsize=(10, 10))
nx.draw(G, visual_positions, with_labels=False, node_color="lightgray", edge_color="gray", node_size=500, font_size=8)

nx.draw_networkx_nodes(G, visual_positions, nodelist=player1_nodes, node_color="red", node_size=500)
nx.draw_networkx_nodes(G, visual_positions, nodelist=player2_nodes, node_color="blue", node_size=500)

#Uncomment this line to show the (q,r) positions of the nodes
for (q, r), node in node_positions.items(): plt.text(visual_positions[node][0], visual_positions[node][1], f"({q},{r})", fontsize=8, ha='center', va='center', color="black", fontweight="bold")

plt.title("2-Player Chinese Checkers Board")
plt.show()
