# This is the agents of the Connect-4 project
# Every agent must be warped into a def function
# The signiture must be algo(int[][] board, int who_next) -> int

import numpy as np
import helper

# an example agent who moves randomly
def agent_random(b, n):
    l, t = helper.get_avalible_column(b)
    play = np.arange(len(l))[l == True]
    return play[int(np.random.rand()*len(play))]

# an exmaple agent who accepts user input
def agent_user(b, n):
    l, t = helper.get_avalible_column(b)
    play = np.arange(len(l))[l == True]
    print(f'Player {n} goes next: ', end='')
    while (True):
        n = input()
        if n == '':
            continue
        n = int(n)
        if n in play:
            return n
        else:
            print(f'Invalid move; try somewhere else...')
            print(f'Avalible columns: {play}')