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
from board import *

STREAK = cfg.STREAK

class Minimax(object):
    """ Minimax object that takes a current connect four board state
    """
    
    def __init__(self, color, num_streak=STREAK):
        # copy the board to self.board
        #self.board = [x[:] for x in board]
        self.color = color
        self.num_streak = num_streak
            
    def best_move(self, depth, state, color):
        """ 
            In current board "state", player in "color" foresees "depth" step further
            and gets the best action
        """
        opp_color = 'x' if color == 'o' else 'o'

        # enumerate all legal moves
        legal_moves = available_moves(state)
        
        # if this node (state) is a terminal node or depth == 0...
        if depth == 0 or len(legal_moves) == 0:
            # return the heuristic value of node
            return None, self.value(state, color)
      
        move_value = {}
        for move in legal_moves:
            next_board = calc_next_board(state, move, color)
            _, v = self.best_move(depth-1, next_board, opp_color)
            move_value[move] = v

        max_or_min = max if self.color==color else min # determine whether this player is maximizer or minimizer
        opt_value = max_or_min(move_value.values())
        tie = [move for move in legal_moves if move_value[move] == opt_value]
        opt_move = random.choice(tie)
        
        return opt_move, opt_value
        
    def value(self, state, color):
        """ Simple heuristic to evaluate board configurations
            Heuristic is (num of 4-in-a-rows)*99999 + (num of 3-in-a-rows)*100 + 
            (num of 2-in-a-rows)*10 - (num of opponent 4-in-a-rows)*99999 - (num of opponent
            3-in-a-rows)*100 - (num of opponent 2-in-a-rows)*10
        """

        opp_color = 'x' if color == 'o' else 'o'

        n_streaks  = [check_streak(state, color, streak) for streak in range(2,self.num_streak+1)]
        value = 0
        for i, v in enumerate(n_streaks[:-1]):
            value += v*100**i
        # termination condition
        value += n_streaks[-1]*1e15

        opp_n_streaks  = [check_streak(state, opp_color, streak) for streak in range(2,self.num_streak+1)]
        for i, v in enumerate(opp_n_streaks[:-1]):
            value -= v*100**i

        if opp_n_streaks[-1] != 0:
            value = -1e7

#        import time
#        print([i for i in range(2,self.num_streak+1)])
#        print(n_streaks)
#        print(opp_n_streaks, value)
#        time.sleep(.3)
#        for row in state:
#            print(row)

        return value
            
            
