import numpy as np                
import copy
import cfg
HEIGHT = cfg.HEIGHT
WIDTH = cfg.WIDTH

def check_streak(state, color, streak):
    count = 0
    # for each piece in the board...
    for i in range(HEIGHT):
        for j in range(WIDTH):
            # ...that is of the color we're looking for...
            if state[i][j].lower() == color.lower():
                # check if a vertical streak starts at (i, j)
                count += check_up(state, i, j, streak)
                
                # check if a horizontal four-in-a-row starts at (i, j)
                count += check_right(state ,i, j, streak)
                
                # check if a diagonal up four-in-a-row starts at (i, j)
                count += check_diagonal_up(state ,i, j, streak)

                # check if a diagonal down  four-in-a-row starts at (i, j)
                count += check_diagonal_down(state ,i, j, streak)
    # return the sum of streaks of length 'streak'
    return count

def check_up(board, row, col, streak):
    consecutive = 0
    for i in range(row, HEIGHT):
        if board[i][col] == board[row][col]:
            consecutive += 1
        else:
            break

    if consecutive >= streak:
        return True
    else:
        return False

def check_right(board, row, col, streak):
    
    consecutive = 0
    for j in range(col, WIDTH):
        if board[row][j] == board[row][col]:
            consecutive += 1
        else:
            break

    if consecutive >= streak:
        return True
    else:
        return False

def check_diagonal_up(board, row, col, streak):
    #↗
    # check for diagonals with positive slope
    consecutive = 0
    for i in range(streak):
        if row + i >= HEIGHT-1 or col + i >= WIDTH-1:
            break
        elif board[row+i][row+i] == board[row][col]:
            consecutive += 1
        else:
            break
        
    if consecutive >= streak:
        return True
    else:
        return False

def check_diagonal_down(board, row, col, streak):
    # check for diagonals with negative slope
    consecutive = 0
    for i in range(streak):
        if row + i <= 0 or col + i >= WIDTH-1:
            break
        elif board[row-i][col+i].lower() == board[row][col].lower():
            consecutive += 1
        else:
            break

    if consecutive >= streak:
        return True
    else:
        return False

def calc_next_board(state, column, color):
    """ 
        Change a state object to reflect a player, denoted by color,
        making a move at column 'column'
        
        Returns a copy of new state array with the added move
    """
    next_board = copy.deepcopy(state)
    for i in range(HEIGHT):
        if next_board[i][column] == ' ':
            next_board[i][column] = color
            break
    return next_board

def available_moves(state):
    '''
    board[-1] is highest row
    params
        board : 2D array representing connect4 board
    return
        (numpy array) : index of columns that are not full.
    '''
    return np.argwhere(np.array(state[-1]) == ' ').ravel()
