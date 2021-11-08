# Python Final Project
# Connect Four
#
# Erik Ackermann
# Charlene Wang
#
# Connect 4 Module
# February 27, 2012

import random
import cfg

STREAK = cfg.STREAK

class Minimax(object):
    """ Minimax object that takes a current connect four board state
    """
    
    def __init__(self, board, color, num_streak=STREAK):
        # copy the board to self.board
        #self.board = [x[:] for x in board]
        self.board = board

        self.board_height = len(board)
        self.board_width = len(board[0])
        self.color = color
        self.opp_color = 'x' if color == 'o' else 'o'
        self.num_streak = num_streak
            
    def bestMove(self, depth, state, color):
        """ 
            In current board "state", player in "color" foresees "depth" step further
            and gets the best action
        """

        # Opponent
        opp_color = 'x' if color == 'o' else 'o'

        # enumerate all legal moves
        legal_moves = [] # will map legal move states to their alpha values
        for col in range(self.board_width):
            # if column i is a legal move...
            if self.isLegalMove(col, state):
                legal_moves.append(col)
        
        # if this node (state) is a terminal node or depth == 0...
        if depth == 0 or len(legal_moves) == 0:
            # return the heuristic value of node
            return None, self.value(state, color)
      
        move_value = {}
        for move in legal_moves:
            next_board = self.makeMove(state, move, color)
            _, v = self.bestMove(depth-1, next_board, opp_color)
            move_value[move] = v

        max_or_min = max if self.color==color else min # determine whether this player is maximizer or minimizer
        best_value = max_or_min(move_value.values())
        tie = [move for move in legal_moves if move_value[move] == best_value]
        best_move = random.choice(tie)
        
        return best_move, best_value
        
    def isLegalMove(self, column, state):
        """ Boolean function to check if a move (column) is a legal move
        """
        
        for i in range(self.board_height):
            if state[i][column] == ' ':
                # once we find the first empty, we know it's a legal move
                return True
        
        # if we get here, the column is full
        return False
    
    def makeMove(self, state, column, color):
        """ Change a state object to reflect a player, denoted by color,
            making a move at column 'column'
            
            Returns a copy of new state array with the added move
        """
        
        temp = [x[:] for x in state]
        for i in range(self.board_height):
            if temp[i][column] == ' ':
                temp[i][column] = color
                return temp

    def value(self, state, color):
        """ Simple heuristic to evaluate board configurations
            Heuristic is (num of 4-in-a-rows)*99999 + (num of 3-in-a-rows)*100 + 
            (num of 2-in-a-rows)*10 - (num of opponent 4-in-a-rows)*99999 - (num of opponent
            3-in-a-rows)*100 - (num of opponent 2-in-a-rows)*10
        """


        opp_color = "x" if color == "o" else "o"
        
        n_streaks  = [self.checkForStreak(state, color, streak) for streak in range(2,self.num_streak+1)]
        value = 0
        for i, v in enumerate(n_streaks[:-1]):
            value += v*100**i
        # termination condition
        value += n_streaks[-1]*1e20

        opp_n_streaks  = [self.checkForStreak(state, opp_color, streak) for streak in range(2,self.num_streak+1)]
        for i, v in enumerate(opp_n_streaks[:-1]):
            value -= v*100**i

        if opp_n_streaks[-1] != 0:
            value = -1e10

#        import time
#        print([i for i in range(2,self.num_streak+1)])
#        print(n_streaks)
#        print(opp_n_streaks, value)
#        time.sleep(.3)
#        for row in state:
#            print(row)

        return value
            
    def checkForStreak(self, state, color, streak):
        count = 0
        # for each piece in the board...
        for i in range(self.board_height):
            for j in range(self.board_width):
                # ...that is of the color we're looking for...
                if state[i][j].lower() == color.lower():
                    # check if a vertical streak starts at (i, j)
                    count += self.verticalStreak(i, j, state, streak)
                    
                    # check if a horizontal four-in-a-row starts at (i, j)
                    count += self.horizontalStreak(i, j, state, streak)
                    
                    # check if a diagonal (either way) four-in-a-row starts at (i, j)
                    count += self.diagonalCheck(i, j, state, streak)
        # return the sum of streaks of length 'streak'
        return count
            
    def verticalStreak(self, row, col, state, streak):
        consecutiveCount = 0
        for i in range(row, self.board_height):
            if state[i][col].lower() == state[row][col].lower():
                consecutiveCount += 1
            else:
                break
    
        if consecutiveCount >= streak:
            return 1
        else:
            return 0
    
    def horizontalStreak(self, row, col, state, streak):
        consecutiveCount = 0
        for j in range(col, self.board_width):
            if state[row][j].lower() == state[row][col].lower():
                consecutiveCount += 1
            else:
                break

        if consecutiveCount >= streak:
            return 1
        else:
            return 0
    
    def diagonalCheck(self, row, col, state, streak):

        total = 0
        # check for diagonals with positive slope
        consecutiveCount = 0
        
        i=0
        while True:
            if row+i >= self.board_height or col+i >= self.board_width:
                break
            elif state[row+i][col+i].lower() == state[row][col].lower():
                consecutiveCount += 1
            else:
                break
            i+=1
            
        if consecutiveCount >= streak:
            total += 1

        # check for diagonals with negative slope
        consecutiveCount = 0
        i=0
        while True:
            if row-i < 0 or col+i >= self.board_width:
                break
            elif state[row-i][col+i].lower() == state[row][col].lower():
                consecutiveCount += 1
            else:
                break
            i += 1 # increment column when row is incremented

        if consecutiveCount >= streak:
            total += 1

        return total

