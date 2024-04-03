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