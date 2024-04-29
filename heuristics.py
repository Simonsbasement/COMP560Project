# All the heuristics. 
# Every heuristic must be warped into a def function
# The signiture must be heuristic(int[][] board, int who_goes_next, int winning_length) -> int score

import numpy as np

import helper

# Example heuristic: always returns zero. 
def h_zero(b, n, w):
    return 0

#TODO: An assortment of heuristics

# Source: https://roboticsproject.readthedocs.io/en/latest/ConnectFourAlgorithm.html
# Heuristic of the sliding window
def h_sliding_windows(b, n, w=4):
    # Provide a score for the sliding window, given the window and who's piece to score for.
    # Input:  int[] window = the sliding window of the length w (as in Connect-w)
    #         int    piece = the ID for the agent to score for
    # Return: int    score = the score of the corrent board, for the agent *piece*
    def evaluate_window(window, n):
        score = 0
        
        counts = []
        for next in range(0, 3):
            count = 0
            for each in window:
                if (np.equal(each, next)):
                    count = count + 1
            counts.append(count)

        # Prioritise a winning move
        # Minimax makes this less important
        if counts[n] == 4:
            score += 1000
        # Make connecting 3 second priority
        elif counts[n] == 3 and counts[0] == 1:
            score += 5
        # Make connecting 2 third priority
        elif counts[n] == 2 and counts[0] == 2:
            score += 2
        # Prioritise blocking an opponent's winning move (but not over bot winning)
        # Minimax makes this less important
        if counts[int(n==1)+1] == 3 and counts[0] == 1:
            score -= 500

        return score

    next = n
    [n, m] = np.shape(np.array(b))

    score = 0

    for c in range(0, n):
        for r in range(0, m):
            if b[c, r] == 0:
                continue
            # check in sequence: up->right->right-up->right-down
            
            #up
            if (r < m-w+1):
                window = b[c, r:r+w]
                score += evaluate_window(window, next)
            
            #right
            if (c < n-w+1):
                window = b[c:c+w, r]
                score += evaluate_window(window, next)
            
            #right-up
            if (r < m-w+1 and c < n-w+1):
                window = [b[c + i, r + i] for i in range(w)]
                score += evaluate_window(window, next)
            
            #right-down
            if (r >= w-1 and c < n-w+1):
                window = [b[c + i, r - i] for i in range(w)]
                score += evaluate_window(window, next)
            
    return score


#Heuristic that prioritizes blocking moves that are close to winning.
def h_threat_detection(b, n, w):
    # Scan the board to identify potential winning moves for both players
    opponent = 1 if n == 2 else 2  # Identify the opponent's player ID
    opponent_threats = []
    ai_opportunities = []

    for col in range(len(b)):
        for row in range(len(b[col])):
            if b[col][row] == 0:
                # Check if placing a piece at this position would create a winning move for the opponent
                b[col][row] = opponent
                opponent_wins = helper.get_winner(b, w)
                b[col][row] = 0  # Reset the board to its original state
                if opponent_wins == opponent:
                    opponent_threats.append((col, row))
                # Check if placing a piece at this position would create a winning move for the AI
                b[col][row] = n
                ai_wins = helper.get_winner(b, w)
                b[col][row] = 0  # Reset the board to its original state
                if ai_wins == n:
                    ai_opportunities.append((col, row))

    # Evaluate the severity of each potential winning move and assign scores
    scores = {}
    for threat in opponent_threats:
        col, row = threat
        # Assign a score based on the proximity of the threat to completion
        scores[(col, row)] = 1000  # High score to prioritize blocking opponent's win

    for opportunity in ai_opportunities:
        col, row = opportunity
        # Assign a score based on the potential for the AI to win
        scores[(col, row)] = 500  # Moderate score for creating AI's own winning opportunity

    # Check if there are potential winning moves detected
    if not scores:
        return 0  # Return default score of 0 if no potential moves detected

    # Choose the move with the highest score as the next move for the AI
    best_move = max(scores, key=scores.get)
    return scores[best_move]  # Return the score of the selected move


#Heuristic that prioritizes placing pieces in the center.
def h_center_control(b, n, w):
    # Define scores for each column based on its position
    column_scores = [2, 3, 4, 5, 4, 3, 2]  # Center columns have higher scores
    
    # Calculate the total score for available moves based on column scores
    total_score = 0
    available_columns, _ = helper.get_avalible_column(b)
    for col, is_available in enumerate(available_columns):
        if is_available:
            total_score += column_scores[col]

    return total_score

# Heuristic that prioritizes blocking opponent's potential forks.
def h_block_fork(b, n, w):
    opponent = 1 if n == 2 else 2  # Identify the opponent's player ID
    
    # Check for potential fork positions for the opponent
    opponent_fork_positions = []
    for col in range(len(b)):
        for row in range(len(b[col])):
            if b[col][row] == 0:
                # Simulate placing a piece at this position for the opponent
                b[col][row] = opponent
                # Check if this move creates a potential fork for the opponent
                if len(helper.get_avalible_column(b)[0]) >= 2:
                    opponent_fork_positions.append((col, row))
                # Reset the board to its original state
                b[col][row] = 0

    # Assign scores to columns based on their ability to block opponent's forks
    column_scores = [0] * len(b)
    for fork_pos in opponent_fork_positions:
        col, _ = fork_pos
        column_scores[col] += 1  # Increment the score for the column

    # Calculate the total score for available moves based on column scores
    total_score = 0
    available_columns, _ = helper.get_avalible_column(b)
    for col, is_available in enumerate(available_columns):
        if is_available:
            total_score += column_scores[col]

    return total_score

# Heuristic that prioritizes moves that lead to a win rather than blocking
def h_offense(b, n, w):
    height = len(b)
    width = len(b[0])
    score = 0

    def count_seq(line, player, seq_len):
        count = 0
        potential_seq = 0
        for i in range(len(line)):
            if line[i] == player:
                potential_seq += 1
            else:
                if potential_seq == seq_len:
                    count += 1
                potential_seq = 0
        if potential_seq == seq_len:
            count += 1
        return count
    
    # Horizontal
    for r in range(height):
        for c in range (width - w + 1):
            horizontal = b[r][c:c + w]
            if 0 in horizontal:
                score += count_seq(horizontal, n, w-1) * 10
                score += count_seq(horizontal, n, w-1) * 5
    
    # Vertical lines (checking only those that can be completed from below)
    for c in range(width):
        for r in range(height - w + 1):
            vertical = [b[r + i][c] for i in range(w)]
            if 0 in vertical:
                score += count_seq(vertical, n, w - 1) * 10
                score += count_seq(vertical, n, w - 2) * 5

    # Diagonal lines (\ and / directions)
    for r in range(height - w + 1):
        for c in range(width - w + 1):
            diag1 = [b[r + i][c + i] for i in range(w)]
            diag2 = [b[r + w - 1 - i][c + i] for i in range(w)]
            if 0 in diag1:
                score += count_seq(diag1, n, w - 1) * 10
                score += count_seq(diag1, n, w - 2) * 5
            if 0 in diag2:
                score += count_seq(diag2, n, w - 1) * 10
                score += count_seq(diag2, n, w - 2) * 5
    return score

# Heuristic that prioritizes moves that block the opponent
def h_defense(b, n, w):
    opponent = 2 if n == 1 else 1
    height = len(b)
    width = len(b[0])
    score = 0

    # Helper function to count threats within a line
    def count_threats(line, opponent, seq_length):
        count = 0
        for i in range(len(line) - seq_length + 1):
            segment = line[i:i+seq_length]
            if segment.count(opponent) == seq_length - 1 and segment.count(0) == 1:
                count += 1
        return count

    # Check all possible lines on the board
    # Horizontal lines
    for r in range(height):
        horizontal = [b[r][c] for c in range(width)]
        score += count_threats(horizontal, opponent, w) * -10

    # Vertical lines
    for c in range(width):
        vertical = [b[r][c] for r in range(height)]
        score += count_threats(vertical, opponent, w) * -10

    # Diagonal lines (\ direction)
    for r in range(height - w + 1):
        for c in range(width - w + 1):
            diag1 = [b[r+i][c+i] for i in range(w)]
            score += count_threats(diag1, opponent, w) * -10

    # Diagonal lines (/ direction)
    for r in range(w - 1, height):
        for c in range(width - w + 1):
            diag2 = [b[r-i][c+i] for i in range(w)]
            score += count_threats(diag2, opponent, w) * -10

    return score