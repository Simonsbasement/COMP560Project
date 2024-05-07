# This is the main of the Connect-4 project. 
# This will function as the game host, calling methods from algorithms.py
# The board will be represented by a 2D array indexed so that m[3][2] will be
#   the 4th column from left(middle column), and 3rd row from bottom.
#   At every cell, 0 means its empty, 1/2 will be the pieces of the corresponding player.
# The host will call agents with algo(board, who_next), and expecting a return
# of a single number, indicating where the agent intends to move next. 
#   Try to make legal moves; if not, the host will ask again; if the same
#   agent produces illegal moves more than # times total, they will be marked as lost.

import time
import numpy as np
from inspect import getmembers, isfunction
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import agents
import helper
import heuristics

# Game host
def main():
    # define size of board; column by row
    c = 7; r = 6
    # w = win by connect #; max_depth = max_depth for agents
    w = 4; max_depth = 5
    # initiate a new game using the same agents when one ends
    forever = False
    # How many games has each player won
    wins = [0, 0]
    # Enumerate through all combanitions of agents and heuristics
    # How many games to play per pair of agent-heuristic
    tournament = True; games_per_pair = 100
    if tournament:
        forever = True
        # Helper for recording the current index of the agent/heuristic
        # tournament_index[0:1] is player 1, tournament_index[0] is their agent,
        #     tournament_index[1] is their heuristic
        tournament_index = [0, 0, 0, 0]
    # Parse all agents into a dict.
    agent_list = getmembers(agents, isfunction)
    # Parse all heuristics into a dict.
    heuristics_list = getmembers(heuristics, isfunction)
    if tournament:
        # Remove agent: user, random
        index = 0
        while (index < len(agent_list)):
            if agent_list[index][0] == 'agent_user' or agent_list[index][0] == 'agent_random':
                agent_list.remove(agent_list[index])
                continue
            index = index+1
        # Remove heuristics: zero
        index = 0
        while (index < len(heuristics_list)):
            if heuristics_list[index][0] == 'h_zero':
                heuristics_list.remove(heuristics_list[index])
                continue
            index = index+1
    
    # Parse names and function calls
    agent_names = [a[0] for a in agent_list]
    agent_funcs = [a[1] for a in agent_list]
    heuristics_names = [a[0] for a in heuristics_list]
    heuristics_funcs = [a[1] for a in heuristics_list]

    print("Welcome to Connect-4!")
    players = []
    their_heuristics = []
    if tournament:
        # Tournament mode
        print("Running tournament mode...")
        print(f"Agents: {agent_names}; count: {len(agent_names)}")
        print(f"Heuristics: {heuristics_names}; count: {len(heuristics_names)}")
        players = [0, 0]
        their_heuristics = [0, 0]
        current_pair_game_count = 0
        pair_accumulated_time = 0.0
    else:
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
            i = input(f'Please select heuristic for agent 1 {agent_names[players[0]]}: {heuristics_names}\n')
            if i == '':
                continue
            i = int(i)
            if (i < 0 or i >= len(heuristics_names)):
                print(f'Invalid heuristic id {i}, try again')
                continue
            else:
                print(f'Agent 1 is now using {heuristics_names[i]}')
                their_heuristics.append(i)
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
        while (True):
            i = input(f'Please select heuristic for agent 2 {agent_names[players[1]]}: {heuristics_names}\n')
            if i == '':
                continue
            i = int(i)
            if (i < 0 or i >= len(heuristics_names)):
                print(f'Invalid heuristic id {i}, try again')
                continue
            else:
                print(f'Agent 2 is now using {heuristics_names[i]}')
                their_heuristics.append(i)
                break
    # Initialize board
    board = np.zeros([c, r], dtype=int)
    if not tournament:
        helper.print_board(board)
    #Start Game timer
    start_time = time.time()
    # which agent is playing
    # mismatch the index in players[next-1] 
    next = 1
    # Game loop
    while (True):
        # Call an agent and get their move
        move = agent_funcs[players[next-1]](board, next, w, heuristics_funcs[their_heuristics[next-1]], max_depth)
        
        # Backtrack from user
        # syntex: b j k
        #           j and k are the columns for the player and agent moves to be backtracked
        if not tournament and not(type(move) == int):
            move = list(move)
            board = helper.backtrack(board, np.int32(move[2]), np.int32(move[4]))
            print(f'Performed backtracking on column {np.int32(move[2])} and {np.int32(move[4])}. ')
            helper.print_board(board)
            continue
        
        # Print the move
        board = helper.make_move(board, next, move)
        if not tournament:
            print(f'Agent {next}: {agent_names[players[next-1]]}|{heuristics_names[their_heuristics[next-1]]} plays: {move}')
            helper.print_board(board)

        # Eval for winner
        winner = helper.get_winner(board, w)
        if winner != 0:
            if not tournament:
                if (winner !=3):
                    # there is a winner!
                    print(f'Winner is agent {winner}: {agent_names[players[winner-1]]}')
                else:
                    # this game is a draw
                    print(f'This game is a DRAW!')
                # Grab game time
                elapsed_time = time.time() - start_time
                elapsed_time_str = "{:.4f}".format(elapsed_time)
                #Record the winner into excel sheet
                helper.record_to_excel(agent_names[players[0]], agent_names[players[1]], winner, elapsed_time_str, heuristics_names[their_heuristics[0]], heuristics_names[their_heuristics[1]], board, max_depth) 
            
            if not forever:
                break
            else:
                if (winner != 3):
                    wins[winner-1] = wins[winner-1] + 1

                if not tournament:
                    print(f'Current wins: {wins[0]} to {wins[1]}')
                else:
                    current_pair_game_count = current_pair_game_count + 1
                    # If this pair is done -> next pair:
                    if current_pair_game_count == games_per_pair:
                        # Grab game time
                        elapsed_time = (time.time() - start_time) / float(games_per_pair)
                        elapsed_time_str = "{:.4f}".format(elapsed_time)
                        # Record to excel
                        if wins[0]+wins[1] <= 1e-6:
                            winrate = 0.0
                        else:
                            winrate = 100.0*float(wins[0])/float(wins[0]+wins[1])
                        print(f'Average time: {elapsed_time_str}; {agent_names[players[0]]}|{heuristics_names[their_heuristics[0]]} vs {agent_names[players[1]]}|{heuristics_names[their_heuristics[1]]}: {winrate}%')
                        helper.record_to_excel(agent_names[players[0]], agent_names[players[1]], winrate, elapsed_time_str, heuristics_names[their_heuristics[0]], heuristics_names[their_heuristics[1]], None, max_depth, tournament=True)
                        # Reset statistics
                        wins = [0, 0]
                        start_time = time.time()
                        current_pair_game_count = 0
                        # next pair
                        tournament_index[3] = tournament_index[3]+1
                        if tournament_index[3] == len(heuristics_names):
                            tournament_index[3] = 0
                            tournament_index[2] = tournament_index[2]+1
                            if tournament_index[2] == len(agent_names):
                                tournament_index[2] = 0
                                tournament_index[1] = tournament_index[1]+1
                                if tournament_index[1] == len(heuristics_names):
                                    tournament_index[1] = 0
                                    tournament_index[0] = tournament_index[0]+1
                                    if tournament_index[0] == len(agent_names):
                                        break
                        players = [tournament_index[0], tournament_index[2]]
                        their_heuristics = [tournament_index[1], tournament_index[3]]
    
                # Initiate a new game when one ends. 
                board = np.zeros([c, r], dtype=int)
                if not tournament:
                    helper.print_board(board)
                next = 1
                continue
        # Flip between agent 1 and 2
        next = int(next == 1) + 1
    return

main()