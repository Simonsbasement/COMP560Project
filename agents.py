# These are the agents of the Connect-4 project
# Every agent must be warped into a def function
# The signiture must be algo(int[][] board, int who_goes_next, int winning_count, func heuristic, int max_depth) -> int column_to_go_next

from mcts import mcts
import numpy as np

import helper

# an example agent who moves randomly
def agent_random(b, n, w, h, d):
    l, t = helper.get_avalible_column(b)
    play = np.arange(len(l))[l]
    return int(play[int(np.random.rand()*len(play))])

# an exmaple agent who accepts user input
def agent_user(b, n, w, h, d):
    l, t = helper.get_avalible_column(b)
    play = np.arange(len(l))[l]
    print(f'Player {n} goes next: ', end='')
    while (True):
        n = input()
        if n == '':
            continue
        if (len(n)>1):
            return n
        n = int(n)
        if n in play:
            return n
        else:
            print(f'Invalid move; try somewhere else...')
            print(f'Avalible columns: {play}')

# Minimax algorithm with Alpha-beta pruning
# Input: int[][] b = board
#        int     n = agent ID (as shown on board) playing FOR
#        int     w = winning by connect w
#        func    h = the heuristic function to evaluate a board
#        int     d = depth limit
# Recursive parameters:
#            final = True if returning to main, else False
#       minimizing = if the current layer is minimizing (as in minimax)
#      alpha, beta = the alpha and beta as in ab-pruning
def agent_minimax(b, n, w, h, d, final=True, minimizing = False, alpha = -9999999, beta = 9999999):
    l, t = helper.get_avalible_column(b)
    play = np.arange(len(l))[l]

    # Make the moves non-deterministic
    # Given non-perfect heuristics
    np.random.shuffle(play)
    
    # If empty board -> going first -> 3 is the optimal move
    if (np.all(t==0)):
        return 3

    # Is more moves be made onto this board?
    is_terminal = not(helper.get_winner(b, w) == 0) or len(play) == 0
    if is_terminal:
        # winning -> high score
        if helper.get_winner(b, w) == n:
            return (None, 9999999)
        # losing -> low score
        elif helper.get_winner(b, w) == int(n==1)+1:
            return (None, -9999999)
        else:
            # No more valid moves, and no winner
            if final:
                # This should NEVER be evaluated if minimax is called from main
                print("TERMINAL at agent_minimax with no winner. ")
            return (None, 0)
    # Depth limit reached, resorting to heuristics 
    if d == 0:
        if final:
            # Why are you using minimax with depth = 0?
            print("Using minimax with depth = 0. Resorting to random. ")
            return agent_random(b, n, w, h, d)
        else:
            return (None, h(b, n, w))
    

    # playing against n -> playing for int(n==1)+1
    if minimizing:
        value = -9999999
        # Randomise column to start
        column = np.random.choice(play)
        for c in play:
            # Create a copy of the board
            b_copy = b.copy()
            # Drop a piece in the temporary board and record score
            b_copy = helper.make_move(b_copy, n, c)
            new_score = agent_minimax(b_copy, n, w, h, d - 1, final = False, minimizing = False, alpha = alpha, beta = beta)[1]
            if new_score > value:
                value = new_score
                # Make 'column' the best scoring column we can get
                column = c
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        if final:
            # This should never happen
            print("Minimax returned move while minimizing.")
            return int(column)
        else:
            return column, value
    # playing for n
    else: 
        value = 9999999
        # Randomise column to start
        column = np.random.choice(play)
        for c in play:
            # Create a copy of the board
            b_copy = b.copy()
            # Drop a piece in the temporary board and record score
            b_copy = helper.make_move(b_copy, int(n==1)+1, c)
            new_score = agent_minimax(b_copy, n, w, h, d - 1, final = False, minimizing = True, alpha = alpha, beta = beta)[1]
            if new_score < value:
                value = new_score
                # Make 'column' the best scoring column we can get
                column = c
            beta = min(beta, value)
            if alpha >= beta:
                break
        if final:
            # Print the eval score (or not)
            # print(f'With score: {h(helper.make_move(b, n, column), n, w)}')
            return int(column)
        else:
            return column, value
    # Should never teach this
    return None


def agent_mcts(board, player, n, w, h, max_depth):
    """
    Function representing the move made by the MCTS agent.

    Args:
    - board: The current state of the game board.
    - player: The player ID of the MCTS agent.
    - n: Number of simulations.
    - w: Number of connected pieces required to win.
    - h: Height of the game board.
    - max_depth: Maximum depth to search.

    Returns:
    The column where the MCTS agent makes its move.
    """
    return mcts(board, n, w, h, max_depth)
