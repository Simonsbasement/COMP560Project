import numpy as np
import helper


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
Monte Carlo Tree Search algorithm.

Args:
- b: The current state of the game board.
- n: Number of simulations.
- w: Number of connected pieces required to win.
- h: Height of the game board.
- max_depth: Maximum depth to search.

Returns:
The next state of the game board after applying MCTS.
"""
def mcts(b, n, w, h, max_depth):
    root = Node(state=b)
    for _ in range(max_depth):
        selected_node = tree_policy(root, w)
        reward = default_policy(selected_node.state, n, w)
        backup(selected_node, reward)
    return best_child(root).state

"""
Select a child node according to the tree policy.

Args:
- node: The current node in the tree.
- w: Number of connected pieces required to win.

Returns:
The selected child node.
"""
def tree_policy(node, w):
    while not helper.get_winner(node.state, w):
        if len(node.children) < len(helper.get_avalible_column(node.state)[0]):
            return expand(node)
        else:
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
    l, _ = helper.get_avalible_column(node.state)
    for c in range(len(l)):
        if l[c]:
            new_state = helper.make_move(np.copy(node.state), 1 if node.state.count(1) <= node.state.count(2) else 2, c)
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
    while not helper.get_winner(state, w):
        l, _ = helper.get_avalible_column(state)
        available_columns = np.arange(len(l))[l]
        move = np.random.choice(available_columns)
        state = helper.make_move(np.copy(state), player, move)
        player = 1 if player == 2 else 2
    winner = helper.get_winner(state, w)
    if winner == player:
        return 1
    elif winner == 0:
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
    while node:
        node.visits += 1
        node.value += reward
        node = node.parent

"""
Select the best child node based on the number of visits.

Args:
- node: The current node in the tree.

Returns:
The state of the best child node.
"""

def best_child(node):
    best_visits = float('-inf')
    best_node = None
    for child in node.children:
        if child.visits > best_visits:
            best_visits = child.visits
            best_node = child
    return best_node.state
