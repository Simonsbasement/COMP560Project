# Helper functions

import os
import numpy as np
import colorama
from colorama import Fore, Style
from openpyxl import Workbook, load_workbook

# Provide check for legal moves and top avalible row. 
# Input: int[][] b = board
# Return: [l, t]
#         bool[] l = boolean array indicating if the corresponding
#                    column is accepting legal move. 
#         int[] t  = int array indicating the top avalible row for
#                    each column. -1 if that column is full (illegal). 
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
# Input: int[][] b = board
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
# Input: int[][] b = board
#        int n = player to make the move
#        int c = which column to move
# Return int[][] b = new board
def make_move(b, n, c):
    b = np.copy(b)
    l, t = get_avalible_column(b)
    play = np.array(range(0, len(l)))[l]
    if c not in play:
        raise ValueError(f'Move {c} is an illegal move out of {play}.')
    else:
        b[c, t[c]] = n
        return b

# Backtrack move j and k
# Input: int[][] b = board
#        int j = one of the columns to backtrack
#        int k = the other column to backtrack
# Return int[][] b = new board
def backtrack(b, j, k):
    _, t = get_avalible_column(b)
    b[j][t[j]-1] = 0
    _, t = get_avalible_column(b)
    b[k][t[k]-1] = 0
    return b

# return 0 for no winner, 1/2 for respective winner
# evaled from 1) bot to top, then 2) left to right
# if there are more than 1 winner on board(idk how), return the 1st discovered winner
# Input: int[][] b = borad
#        int w = connect #
# Return: int winner = 1 or 2 if that player is winning, or 0 if noone is winning
def get_winner(b, w):
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



def record_to_excel(agent1, agent2, winner, first_player, match_time, heuristic, final_board):
    file_name = "game_data.xlsx"

    # Convert final_board to a string
    final_board_str = '\n'.join([' '.join(map(str, row)) for row in final_board])
    
    # Check if the file exists
    if os.path.exists(file_name):
        wb = load_workbook(file_name)
        ws = wb.active
    else:
        # Create a new workbook if the file doesn't exist
        wb = Workbook()
        ws = wb.active
        
        # Define column headers for the new file
        headers = ["Agent 1", "Agent 2", "Winner", "First Player", "Match Time", "Heuristic", "Final Board"]
        for col, header in enumerate(headers, start=1):
            ws.cell(row=1, column=col, value=header)

    # Append data to the next row
    row_data = [agent1, agent2, winner, first_player, match_time, heuristic, final_board_str]
    ws.append(row_data)
    
    # Save the workbook
    wb.save(file_name)
    
    print(f"Data appended to {file_name}")

# # Example usage
# agent1 = "Agent 1"
# agent2 = "Agent 2"
# winner = "Agent 1"
# first_player = "Agent 1"
# match_time = "00:05:23"  # Example match time
# heuristic = "Heuristic 1"  # Example heuristic
# final_board = [[1, 0, 2, 0, 0, 0],
#                [2, 1, 1, 0, 0, 0],
#                [1, 2, 2, 0, 0, 0],
#                [2, 1, 2, 0, 0, 0],
#                [1, 2, 1, 0, 0, 0],
#                [2, 1, 1, 0, 0, 0]]  # Example final board state

# record_to_excel(agent1, agent2, winner, first_player, match_time, heuristic, final_board)