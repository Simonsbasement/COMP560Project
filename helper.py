# Helper functions

import numpy as np
import colorama
from colorama import Fore, Style

# return which columns are accepting legal moves in boolean array
# t is the index of the top avalible row for the avalible columns
def get_avalible_column(b):
    [n, m] = np.shape(np.array(b))
    l = []
    t = []
    for c in range(0, n):
        l.append(False)
        t.append(-1)
        for r in range(0, m):
            if b[c][r] == 0:
                l[-1] = True
                t[-1] = r
                break
    return np.array(l, dtype=bool), np.array(t, dtype=int)

# Print the board
def print_board(b):
    [n, m] = np.shape(np.array(b))
    for r in range(m-1, -1, -1):
        for c in range(0, n):
            match (b[c][r]):
                case 0:
                    print(f'{Fore.WHITE}_ {Style.RESET_ALL}', end='')
                case 1:
                    print(f'{Fore.RED}1 {Style.RESET_ALL}', end='')
                case 2:
                    print(f'{Fore.GREEN}2 {Style.RESET_ALL}', end='')
        print()
    return

# Play a move, return the new board; raise ValueError if trying to make an illegal move
def make_move(b, n, c):
    l, t = get_avalible_column(b)
    play = np.array(range(0, len(l)))[l]
    if c not in play:
        raise ValueError(f'Move {c} is an illegal move.')
    else:
        b[c][t[c]] = n
        return b

# return 0 for no winner, 1/2 for respective winner
# evaled from 1) bot to top, then 2) left to right
# if there are more than 1 winner on board(idk how), return the 1st discovered winner
# TODO
def get_winner(b, w=4):
    [n, m] = np.shape(np.array(b))
    for c in range(0, n):
        for r in range(0, m):
            if b[c][r] == 0:
                continue
            # check in sequence: up->right->right-up->right-down
            conn = [1, 1, 1, 1]
            #up
            for rr in range(r+1, m):
                if (b[c][rr] == b[c][r]):
                    conn[0] = conn[0]+1
                else:
                    break
            #right
            for rr in range(c+1, n):
                if (b[rr][r] == b[c][r]):
                    conn[1] = conn[1]+1
                else:
                    break
            #right-up
            for rr in range(1, min(n-c, m-r)):
                if (b[c+rr][r+rr] == b[c][r]):
                    conn[2] = conn[2]+1
                else:
                    break
            #right-down
            for rr in range(1, min(n-c, r+1)):
                if (b[c+rr][r-rr] == b[c][r]):
                    conn[3] = conn[3]+1
                else:
                    break
            # if win, return winner
            for k in conn:
                if k == w:
                    return b[c][r]
    # if no winner, return 0
    return 0
        

