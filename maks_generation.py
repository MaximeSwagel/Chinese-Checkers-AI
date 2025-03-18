import networkx as nx

def generate_board(hex_layers=9, player_layers=4):
    """
    Generates the board graph and maps between board coordinates and bit indices.
    The board is built in two parts: an expanding (top) half and a contracting (bottom) half.
    """
    G = nx.Graph()
    pos2i = {}
    i2pos = {}
    idx = 0
    last_row = []
    
    # Build top (expanding) half
    for r in range(hex_layers):
        row = []
        for q in range(-r, r+1, 2):
            pos2i[(q, r)] = idx
            i2pos[idx] = (q, r)
            G.add_node(idx)
            row.append(idx)
            idx += 1
        if r > 0:
            for i, node in enumerate(row):
                if i > 0:
                    G.add_edge(node, row[i-1])
                if i < len(last_row):
                    G.add_edge(node, last_row[i])
                if i > 0:
                    G.add_edge(node, last_row[i-1])
        last_row = row

    buffer_rows = []
    # Build bottom (contracting) half
    for r in range(hex_layers, 2*hex_layers - 1):
        row = []
        for q in range(-(2*hex_layers - r - 2), 2*hex_layers - r - 1, 2):
            pos2i[(q, r)] = idx
            i2pos[idx] = (q, r)
            G.add_node(idx)
            row.append(idx)
            idx += 1
        # Connect current row with previous row(s)
        for i, prev in enumerate(last_row):
            qp, rp = i2pos[prev]
            if i == 0:
                directions = [(1, 1)]
            elif i == len(last_row) - 1:
                directions = [(-1, 1)]
            else:
                directions = [(1, 1), (-1, 1)]
            for dq, dr in directions:
                neighbor_coord = (qp + dq, rp + dr)
                if neighbor_coord in pos2i:
                    G.add_edge(prev, pos2i[neighbor_coord])
        # Connect horizontally in the current row
        for i in range(len(row)-1):
            G.add_edge(row[i], row[i+1])
        buffer_rows.append(row)
        if len(buffer_rows) > player_layers:
            buffer_rows.pop(0)
        last_row = row

    return G, pos2i, i2pos

def generate_masks(hex_layers=9, player_layers=4):
    """
    Returns two lists:
      - neighbors_masks: For each board cell, an integer whose bits represent its immediate neighbors.
      - jump_masks: For each board cell, an integer whose bits represent jump destinations 
                    (i.e. extending the neighbor direction by the same vector).
    """
    G, pos2i, i2pos = generate_board(hex_layers, player_layers)
    total_nodes = len(i2pos)
    
    neighbors_masks = [0] * total_nodes
    jump_masks = [0] * total_nodes
    
    for i in range(total_nodes):
        # Compute neighbor mask: for each adjacent node, set its bit.
        nmask = 0
        for j in G.neighbors(i):
            nmask |= (1 << j)
        neighbors_masks[i] = nmask

        # Compute jump mask: for each neighbor, "double" the offset and check if the target exists.
        jmask = 0
        for j in G.neighbors(i):
            dq = i2pos[j][0] - i2pos[i][0]
            dr = i2pos[j][1] - i2pos[i][1]
            jump_coord = (i2pos[j][0] + dq, i2pos[j][1] + dr)
            if jump_coord in pos2i:
                jump_index = pos2i[jump_coord]
                jmask |= (1 << jump_index)
        jump_masks[i] = jmask

    return neighbors_masks, jump_masks

if __name__ == "__main__":
    # Generate the two masks lists.
    neighbors_masks_list, potential_jumps_list = generate_masks()

    # Print neighbor masks
    print("neighbors_masks_list = [")
    for mask in neighbors_masks_list:
        print(f"    {bin(mask)[2:].zfill(81)},")
    print("]\n")

    # Print potential jump masks
    print("potential_jumps_list = [")
    for mask in potential_jumps_list:
        print(f"    {bin(mask)[2:].zfill(81)},")
    print("]")
