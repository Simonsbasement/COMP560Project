# This is the main of the Connect-4 project. 
# This will function as the game host, calling methods from algorithms.py
# The board will be represented by a 2D array indexed so that m[3][2] will be
#   the 4th column from left(middle column), and 3rd row from bottom.
#   At every cell, 0 means its empty, 1/2 will be the pieces of the corresponding player.
# The host will call agents with algo(board, who_next), and expecting a return
# of a single number, indicating where the agent intends to move next. 
#   Try to make legal moves; if not, the host will ask again; if the same
#   agent produces illegal moves more than # times total, they will be marked as lost.

import numpy as np
from inspect import getmembers, isfunction

import agents
import helper
# TODO: parse the heuristics
import heuristics

# Game host main loop
def main():
    # define size of board
    c = 7; r = 6
    # w = connect #; d = max_depth
    w = 4; max_depth = 3
    # Parse all agents into a dict.
    agent_list = getmembers(agents, isfunction)
    agent_names = [a[0] for a in agent_list]
    agent_funcs = [a[1] for a in agent_list]

    print("Connect-4")
    players = []
    while (True):
        i = input(f'Please select agent 1 (who goes first): {agent_names}\n')
        if i == '':
            continue
        i = int(i)
        if (i < 0 or i >= len(agent_names)):
            print(f'Invalid player id {i}, try again')
            continue
        else:
            print(f'Agent 1 is {agent_names[i]}')
            players.append(i)
            break
    while (True):
        i = input(f'Please select agent 2 (who goes second): {agent_names}\n')
        if i == '':
            continue
        i = int(i)
        if (i < 0 or i >= len(agent_names)):
            print(f'Invalid agent id {i}, try again')
            continue
        else:
            print(f'Agent 2 is {agent_names[i]}')
            players.append(i)
            break
    
    board = np.zeros([c, r], dtype=int)
    helper.print_board(board)
    # next serves as the index for players[] 
    # next == 0 is player 1; next == 1 is player 2
    next = 0
    while (True):
        #TODO: parse the heuristics
        move = agent_funcs[players[next]](board, next+1, None, max_depth)
        board = helper.make_move(board, next+1, move)
        print(f'Agent {next+1}: {agent_names[players[next]]} plays: {move}')
        helper.print_board(board)

        winner = helper.get_winner(board, w)
        if winner != 0:
            print(f'Winner is agent {winner}: {agent_names[players[winner-1]]}')
            
            break
            # Initiate a new game when one ends. 
            # board = np.zeros([c, r], dtype=int)
            # helper.print_board(board)
            # next = 0
            # continue
            
        
        if next == 0:
            next = 1
        else:
            next = 0

    

    return


main()