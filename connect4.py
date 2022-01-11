import random
import os
from player import *
import cfg
import numpy as np
import logging
from board import *

class Game(object):
    """ Game object that holds state of Connect n board and game values
    """
    
    board = None
    round = None
    finished = None
    winner = None
    turn = None
    players = [None, None]
    game_name = u"Connecter Quatre\u2122" # U+2122 is "tm" this is a joke
    colors = [-1, 1]
    
    def __init__(self, width = cfg.WIDTH, height = cfg.HEIGHT, streak = cfg.STREAK, verbose=True):
        self.round = 1
        self.finished = False
        self.winner = None
        self.width = width
        self.height = height
        self.verbose = verbose
        self.streak = streak
        
        # logging
        logging.basicConfig(format='%(message)s', level=logging.DEBUG if verbose else logging.INFO) 
        self.logger = logging.getLogger("connect4")
        self.handler = logging.StreamHandler()
        self.handler.setLevel(logging.DEBUG if verbose else logging.INFO) 
        
        self.formatter = logging.Formatter('%(message)s')
        self.handler.setFormatter(self.formatter)
        
        self.board = []
        for i in range(self.height):
            self.board.append([])
            for j in range(self.width):
                self.board[i].append(0)

    def set_player(self, p1, p2):
        self.players = [p1,p2]
        self.logger.debug("{0} will be {1}".format(self.players[0].name, self.colors[0]))
        self.logger.debug("{0} will be {1}".format(self.players[1].name, self.colors[1]))

        # x always goes first (arbitrary choice on my part)
        self.turn = self.players[0]
        
    
    def new_game(self):
        """ Function to reset the game, but not the names or colors
        """
        self.round = 1
        self.finished = False
        self.winner = None
        
        # x always goes first (arbitrary choice on my part)
        self.turn = self.players[0]
        
        self.board = []
        for i in range(self.height):
            self.board.append([])
            for j in range(self.width):
                self.board[i].append(0)

    def switch_turn(self):
        if self.turn == self.players[0]:
            self.turn = self.players[1]
        else:
            self.turn = self.players[0]

        # increment the round
        self.round += 1

    def play_round(self):
        player = self.turn

        if self.round > self.width*self.height:
            self.winner = None
            self.finished = True
            return
    
        # move is the column that player want's to play
        self.logger.debug("{0}'s turn.  {0} is {1}".format(player.name, player.color))
        move = player.move(self.board)
        for i in range(self.height):
            try:
                if self.board[i][move] == 0:
                    self.board[i][move] = player.color
                    self.find_streak()
                    self.switch_turn()
                    if self.verbose:
                        self.print_state()
                    return
            except TypeError:
                print(f'{player.name = }, {i = }, {move = }')
                exit()
        # if we get here, then the column is full
        self.logger.debug("Invalid move (column is full)")
        return
    
    def find_streak(self):
        """ Finds start i,j of four-in-a-row
            Calls highlight_streak
        """

        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] == 0:
                    continue
                else:
                    # check the 3 streaks
                    functions = [check_up, check_right, check_diagonal_up, check_diagonal_down]
                    for f in functions:
                        if f(self.board, i,j, self.streak):
                            self.winner = self.players[0] if self.players[0].color == self.board[i][j] else self.players[1]
                            self.finished = True
                            return i, j, f # row, column, function

        return None
    
    def highlight_streak(self, board):
        """ This function enunciates four-in-a-rows by capitalizing
            the character for those pieces on the board
        """
        if self.find_streak() ==  None:
            return board

        row, col, f = self.find_streak() 
        if f == check_up:
            for i in range(self.streak):
                board[row+i][col] = board[row+i][col].upper()
        
        elif f == check_right:
            for i in range(self.streak):
                board[row][col+i] = board[row][col+i].upper()
        
        elif f == check_diagonal_up:
            for i in range(self.streak):
                board[row+i][col+i] = board[row+i][col+i].upper()
        
        elif f == check_diagonal_down:
            for i in range(self.streak):
                board[row-i][col+i] = board[row-i][col+i].upper()

        return board
    
    def print_state(self, stats=None, encoding=True):
        # cross-platform clear screen
#        os.system( [ 'clear', 'cls' ][ os.name == 'nt' ] )
#        self.logger.debug(u"{0}!".format(self.game_name))
        self.logger.debug("Round: " + str(self.round))

        encoded_board = copy.deepcopy(self.board)

        for i in range(self.height):
            for j in range(self.width):
                if encoded_board[i][j] == 0: 
                    encoded_board[i][j] = ' ' 
                elif encoded_board[i][j] == -1:
                    encoded_board[i][j] = 'x'
                else:
                    encoded_board[i][j] = 'o'

        if self.finished:
            encoded_board = self.highlight_streak(encoded_board)

        for i in range(self.height-1, -1, -1):
            print("\t", end="")
            for j in range(self.width):
                print("| " + str(encoded_board[i][j]), end=" ")
            print("|")
        self.logger.debug("\t "+" _  "*self.width)
        column_string = ''
        for i in range(1,self.width+1):
            column_string += f' {i}  '
        self.logger.debug("\t " + column_string)
        if stats is not None:
            print("{0}: {1} wins, {2}: {3} wins, {4} ties".format(
                        self.players[0].name, stats[0],self.players[1].name, stats[1], stats[2]))

        if self.finished:
            self.logger.debug("Game Over!")
            if self.winner != None:
                self.logger.debug(str(self.winner.name) + " is the winner")
            else:
                self.logger.debug("Game was a draw")
