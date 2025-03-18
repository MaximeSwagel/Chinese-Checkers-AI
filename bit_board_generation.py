from game_board import generate_two_player_chinese_checkers

def generate_bitboard(hex_layers, player_layers):
    """
    Using the hexagonal grid to generate bitboard representations for Chinese checkers
    """
    G, node_positions, player1_nodes, player2_nodes = generate_two_player_chinese_checkers(hex_layers, player_layers)
    
    # Create bitboard mapping
    # 0b000000000000000000000000000000000000000000000000000000000000000000000000000000000
    bitboard_mapping = {index: 1 << index for index in node_positions.values()}
    
    # Initialize bitboards
    # Player one
    # 0b000000000000000000000000000000000000000000000000000000000000000000000001111111111
    bitboard_player1 = sum(bitboard_mapping[node] for node in player1_nodes)
    # 0b111111111100000000000000000000000000000000000000000000000000000000000000000000000
    bitboard_player2 = sum(bitboard_mapping[node] for node in player2_nodes)
    # Using logical or we can combine they two to get all the pieces
    # 0b111111111100000000000000000000000000000000000000000000000000000000000001111111111
    bitboard_occupied = bitboard_player1 | bitboard_player2
    
    # Precompute move masks
    neighbors_masks = {} # This stores the masks for the neightbors for each node
    jump_masks = {} # This stores the masks for the potential jumps for each node

    # Loop through the neighbor nodes of the current node
    for node in node_positions.values():
        neighbors_mask = 0
        jump_mask = 0
        for neighbor in G.neighbors(node):
            bit_pos = bitboard_mapping[neighbor]
            neighbors_mask |= bit_pos
            
            # Determine potential jump positions, meaning two steps in a straight line
            # Step 1 get coordinate of current node
            q1, r1 = [key for key, value in node_positions.items() if value == node][0]
            # Step 2 get coordinates of the neighbor that we want to jump over
            q2, r2 = [key for key, value in node_positions.items() if value == neighbor][0]
            # Calculate the coordinates of the node opposite the neighbor we jump
            q_jump, r_jump = 2 * q2 - q1, 2 * r2 - r1
            # Ccheck if the landing position exists on the board, if so add it to the mask
            if (q_jump, r_jump) in node_positions:
                jump_pos = bitboard_mapping[node_positions[(q_jump, r_jump)]]
                jump_mask |= jump_pos
        
        neighbors_masks[node] = neighbors_mask
        jump_masks[node] = jump_mask
    
    return bitboard_mapping, bitboard_player1, bitboard_player2, bitboard_occupied, neighbors_masks, jump_masks, node_positions

def print_bitboard_binary(bitboard):
    """
    Print the bitboard as a 0b binary string, padded to 81 bits.
    """
    print("0b" + bin(bitboard)[2:].zfill(81) + ",")

if __name__ == "__main__":
    hex_layers = 9
    player_layers = 4
    
    (bitboard_mapping, bitboard_player1, bitboard_player2, 
     bitboard_occupied, neighbors_masks, jump_masks, node_positions) = generate_bitboard(hex_layers, player_layers)

    for i in range(81):
        test_pos = list(node_positions.values())[i]
        print_bitboard_binary(neighbors_masks[test_pos])

    print()

    for i in range(81):
        test_pos = list(node_positions.values())[i]
        print_bitboard_binary(jump_masks[test_pos])

    print(node_positions)

