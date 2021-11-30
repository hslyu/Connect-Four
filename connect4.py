import random
import os
from player import *
import cfg
import numpy as np
import logging
from board import *

WIDTH = cfg.WIDTH
HEIGHT = cfg.HEIGHT
STREAK = cfg.STREAK

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
    colors = ["x", "o"]
    
    def __init__(self, width = WIDTH, height = HEIGHT, streak = STREAK, verbose=True):
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
                self.board[i].append(' ')

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
                self.board[i].append(' ')

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
                if self.board[i][move] == ' ':
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
                if self.board[i][j] == ' ':
                    continue
                else:
                    # check if a vertical four-in-a-row starts at (i, j)
                    if check_up(self.board, i, j, self.streak):
                        self.winner = self.players[0] if self.players[0].color == self.board[i][j].lower() else self.players[1]
                        self.highlight_streak(i, j, 'vertical')
                        self.finished = True
                        return
                    # check if a horizontal four-in-a-row starts at (i, j)
                    elif check_right(self.board, i, j, self.streak):
                        self.winner = self.players[0] if self.players[0].color == self.board[i][j].lower() else self.players[1]
                        self.highlight_streak(i, j, 'horizontal')
                        self.finished = True
                        return
                    elif check_diagonal_up(self.board, i, j, self.streak):
                        self.winner = self.players[0] if self.players[0].color == self.board[i][j].lower() else self.players[1]
                        self.highlight_streak(i, j, 'diagonal_up')
                        self.finished = True
                        return
                    elif check_diagonal_down(self.board, i, j, self.streak):
                        self.winner = self.players[0] if self.players[0].color == self.board[i][j].lower() else self.players[1]
                        self.highlight_streak(i, j, 'diagonal_down')
                        self.finished = True
                        return
    
    def highlight_streak(self, row, col, direction):
        """ This function enunciates four-in-a-rows by capitalizing
            the character for those pieces on the board
        """
        
        if direction == 'vertical':
            for i in range(self.streak):
                self.board[row+i][col] = self.board[row+i][col].upper()
        
        elif direction == 'horizontal':
            for i in range(self.streak):
                self.board[row][col+i] = self.board[row][col+i].upper()
        
        elif direction == 'diagonal_up':
            for i in range(self.streak):
                self.board[row+i][col+i] = self.board[row+i][col+i].upper()
        
        elif direction == 'diagonal_down':
            for i in range(self.streak):
                self.board[row-i][col+i] = self.board[row-i][col+i].upper()
        
        else:
            self.logger.debug("Error - Cannot enunciate four-of-a-kind")
    
    def print_state(self, stats=None):
        # cross-platform clear screen
#        os.system( [ 'clear', 'cls' ][ os.name == 'nt' ] )
#        self.logger.debug(u"{0}!".format(self.game_name))
        self.logger.debug("Round: " + str(self.round))

        for i in range(self.height-1, -1, -1):
            print("\t", end="")
            for j in range(self.width):
                print("| " + str(self.board[i][j]), end=" ")
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
