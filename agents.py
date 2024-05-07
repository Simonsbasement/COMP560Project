# These are the agents of the Connect-4 project
# Every agent must be warped into a def function
# The signiture must be algo(int[][] board, int who_goes_next, int winning_count, func heuristic, int max_depth) -> int column_to_go_next

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

"""
    Function representing the move made by the MCTS agent.

    Args:
    - board: The current state of the game board.
    - n: Number of simulations.
    - w: Number of connected pieces required to win.
    - h: [current implementation does not care about any heuristics
          all games simulated are random games]
    - max_depth: Maximum depth to search.

    Returns:
    The column where the MCTS agent makes its move.
"""
def agent_mcts(b, n, w, h, max_depth):
    # Local helpers for mcts
    """
    Initialize a Node object.

    Args:
    - state: The state of the game board.
    - parent: The parent node of the current node.
    """
    class Node:
        def __init__(self, state, parent=None):
            self.state = state
            self.parent = parent
            self.children = []
            self.visits = 0
            self.value = 0
    
    """
    Select a child node according to the tree policy.

    Args:
    - node: The current node in the tree.
    - w: Number of connected pieces required to win.

    Returns:
    The selected child node.
    """
    def tree_policy(node, w):
        # while there is no winner in node.state
        while not helper.get_winner(node.state, w):
            # if there are any next moves not investigated:
            if len(node.children) < len(helper.get_avalible_column(node.state)[0]):
                # generate, associate, and return a (next) child of the node
                return expand(node)
            else:
                # else select and return the best child of the current node
                # -> depth +1
                node = best_uct(node)
        return node

    """
    Expand the tree by adding a new child node.

    Args:
    - node: The node to expand.

    Returns:
    The newly added child node.
    """
    def expand(node):
        # get which columns are legal next moves
        l, _ = helper.get_avalible_column(node.state)
        # for the left-most legal next move:
        for c in range(len(l)):
            if l[c]:
                # make a child based on that move, associate child to parent, return the child
                new_state = helper.make_move(np.copy(node.state), 1 if node.state.tolist().count(1.0) <= node.state.tolist().count(2.0) else 2, c)
                new_node = Node(state=new_state, parent=node)
                node.children.append(new_node)
                return new_node

    """
    Select the child node with the best UCT value.

    Args:
    - node: The current node in the tree.

    Returns:
    The selected child node.
    """
    def best_uct(node):
        max_uct = float('-inf')
        selected_node = None
        for child in node.children:
            uct = (child.value / child.visits) + np.sqrt(2 * np.log(node.visits) / child.visits)
            if uct > max_uct:
                max_uct = uct
                selected_node = child
        return selected_node

    """
    Default policy to simulate a game from a given state.

    Args:
    - state: The current state of the game board.
    - player: The current player.
    - w: Number of connected pieces required to win.

    Returns:
    The reward obtained after simulating the game.
    """
    def default_policy(state, player, w):
        # simulate (1) random game based on state
        while not helper.get_winner(state, w):
            l, _ = helper.get_avalible_column(state)
            available_columns = np.arange(len(l))[l]
            move = np.random.choice(available_columns)
            state = helper.make_move(np.copy(state), player, move)
            player = 1 if player == 2 else 2
        winner = helper.get_winner(state, w)
        # score and return the result of the random game
        if winner == player:
            return 1
        elif winner == 3: # draw is 3
            return 0.5
        else:
            return 0

    """
    Backup the reward value through the tree.

    Args:
    - node: The current node in the tree.
    - reward: The reward to propagate through the tree.
    """
    def backup(node, reward):
        # for node and all its parents:
        while node:
            node.visits += 1
            # accumulate the value of all its childs
            node.value += reward
            node = node.parent

    """
    Select the best child node based on the number of visits.

    Args:
    - node: The current node in the tree.

    Returns:
    The best child node of node.
    """
    def best_child(node):
        best_visits = float('-inf')
        best_node = None
        for child in node.children:
            if child.visits > best_visits:
                best_visits = child.visits
                best_node = child
        return best_node
    
    """
    Monte Carlo Tree Search algorithm core.

    Args:
    - b: The current state of the game board.
    - n: Number of simulations.
    - w: Number of connected pieces required to win.
    - h: Height of the game board.
    - max_depth: Maximum depth to search.

    Returns:
    The next state of the game board after applying MCTS.
    """
    # Create a root node with the given board
    root = Node(state=b)
    # for each allowed depth:
    # ->This implementation uses max_depth as "max count of games simulated"
    # the extras are for guaranteeing at least a full set of 1-depth childs
    for _ in range(max_depth+b.shape[0]):
        # generate a child for root
        # or, if 1-depth child is full, get the current best child through best_uct(node)
        selected_node = tree_policy(root, w)
        # simulate (1) random game based on this child, score the result
        reward = default_policy(selected_node.state, n, w)
        # propagate and accumulate the 1) visit count and 2) value of the child up the tree
        backup(selected_node, reward)
    # get the difference between root's board and its best child's
    state_diff = abs(best_child(root).state - root.state)
    # parse this difference to move, and return
    return int((np.add.reduce(state_diff.reshape((1,-1))).tolist().index(1.0)+0.5)/7)

    


