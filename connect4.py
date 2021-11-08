# Python Final Project
# Connect Four
#
# Erik Ackermann
# Charlene Wang
#
# Connect n Module
# February 27, 2012

import random
import os
from player import *
import cfg
import numpy as np
import logging

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
        
        diff = 1
        # do cross-platform clear screen
        os.system( [ 'clear', 'cls' ][ os.name == 'nt' ] )
        self.players[0] = QPlayer("Player 1", self.colors[0])
#        self.players[0] = HumanPlayer("Player 1", self.colors[0])
        self.logger.debug("{0} will be {1}".format(self.players[0].name, self.colors[0]))
        
        self.players[1] = MiniMaxPlayer("Player 2", self.colors[1], diff+1)
        self.logger.debug("{0} will be {1}".format(self.players[1].name, self.colors[1]))
        
        # x always goes first (arbitrary choice on my part)
        self.turn = self.players[0]
        
        self.board = []
        for i in range(self.height):
            self.board.append([])
            for j in range(self.width):
                self.board[i].append(' ')
    
    def newGame(self):
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

    def switchTurn(self):
        if self.turn == self.players[0]:
            self.turn = self.players[1]
        else:
            self.turn = self.players[0]

        # increment the round
        self.round += 1

    def nextMove(self):
        player = self.turn

        # there are only 42 legal places for pieces on the board
        # exactly one piece is added to the board each turn
        if self.round > self.width*self.height:
            self.finished = True
            # this would be a stalemate :(
            return
        
        # move is the column that player want's to play
        self.logger.debug("{0}'s turn.  {0} is {1}".format(player.name, player.color))
        move = player.move(self.board)

        for i in range(self.height):
            if self.board[i][move] == ' ':
                self.board[i][move] = player.color
                self.switchTurn()
                self.findStreak()
                if self.verbose:
                    self.printState()
                return
        # if we get here, then the column is full
        self.logger.debug("Invalid move (column is full)")
        return
    
    def checkForStreak(self):
        # for each piece in the board...
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] != ' ':
                    # check if a vertical four-in-a-row starts at (i, j)
                    if self.verticalCheck(i, j):
                        self.finished = True
                        return
                    
                    # check if a horizontal four-in-a-row starts at (i, j)
                    if self.horizontalCheck(i, j):
                        self.finished = True
                        return
                    
                    # check if a diagonal (either way) four-in-a-row starts at (i, j)
                    # also, get the slope of the four if there is one
                    diag_fours, slope = self.diagonalCheck(i, j)
                    if diag_fours:
                        self.logger.debug(slope)
                        self.finished = True
                        return
        
    def verticalCheck(self, row, col):#{{{
        #print("checking vert")
        fourInARow = False
        consecutiveCount = 0
    
        for i in range(row, self.height):
            if self.board[i][col].lower() == self.board[row][col].lower():
                consecutiveCount += 1
            else:
                break
    
        if consecutiveCount >= self.streak:
            fourInARow = True
            if self.players[0].color.lower() == self.board[row][col].lower():
                self.winner = self.players[0]
            else:
                self.winner = self.players[1]
    
        return fourInARow
    
    def horizontalCheck(self, row, col):
        fourInARow = False
        consecutiveCount = 0
        
        for j in range(col, self.width):
            if self.board[row][j].lower() == self.board[row][col].lower():
                consecutiveCount += 1
            else:
                break

        if consecutiveCount >= self.streak:
            fourInARow = True
            if self.players[0].color.lower() == self.board[row][col].lower():
                self.winner = self.players[0]
            else:
                self.winner = self.players[1]

        return fourInARow
    
    def diagonalCheck(self, row, col):
        fourInARow = False
        count = 0
        slope = None

        # check for diagonals with positive slope
        consecutiveCount = 0
        j = col
        for i in range(row, self.height):
            if j >= self.width:
                break
            elif self.board[i][j].lower() == self.board[row][col].lower():
                consecutiveCount += 1
            else:
                break
            j += 1 # increment column when row is incremented
            
        if consecutiveCount >= self.streak:
            count += 1
            slope = 'positive'
            if self.players[0].color.lower() == self.board[row][col].lower():
                self.winner = self.players[0]
            else:
                self.winner = self.players[1]

        # check for diagonals with negative slope
        consecutiveCount = 0
        j = col
        for i in range(row, -1, -1):
            if j >= self.width:
                break
            elif self.board[i][j].lower() == self.board[row][col].lower():
                consecutiveCount += 1
            else:
                break
            j += 1 # increment column when row is decremented

        if consecutiveCount >= self.streak:
            count += 1
            slope = 'negative'
            if self.players[0].color.lower() == self.board[row][col].lower():
                self.winner = self.players[0]
            else:
                self.winner = self.players[1]

        if count > 0:
            fourInARow = True
        if count == 2:
            slope = 'both'
        return fourInARow, slope#}}}
    
    def findStreak(self):
        """ Finds start i,j of four-in-a-row
            Calls highlightStreak
        """
    
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] != ' ':
                    # check if a vertical four-in-a-row starts at (i, j)
                    if self.verticalCheck(i, j):
                        self.highlightStreak(i, j, 'vertical')
                        self.finished = True
                        return
                    
                    # check if a horizontal four-in-a-row starts at (i, j)
                    if self.horizontalCheck(i, j):
                        self.highlightStreak(i, j, 'horizontal')
                        self.finished = True
                        return
                    
                    # check if a diagonal (either way) four-in-a-row starts at (i, j)
                    # also, get the slope of the four if there is one
                    diag_fours, slope = self.diagonalCheck(i, j)
                    if diag_fours:
                        self.highlightStreak(i, j, 'diagonal', slope)
                        self.logger.debug(slope)
                        self.finished = True
                        return
    
    def highlightStreak(self, row, col, direction, slope=None):
        """ This function enunciates four-in-a-rows by capitalizing
            the character for those pieces on the board
        """
        
        if direction == 'vertical':
            for i in range(self.streak):
                self.board[row+i][col] = self.board[row+i][col].upper()
        
        elif direction == 'horizontal':
            for i in range(self.streak):
                self.board[row][col+i] = self.board[row][col+i].upper()
        
        elif direction == 'diagonal':
            if slope == 'positive' or slope == 'both':
                for i in range(self.streak):
                    self.board[row+i][col+i] = self.board[row+i][col+i].upper()
        
            elif slope == 'negative' or slope == 'both':
                for i in range(self.streak):
                    self.board[row-i][col+i] = self.board[row-i][col+i].upper()
        
        else:
            self.logger.debug("Error - Cannot enunciate four-of-a-kind")
    
    def printState(self):
        # cross-platform clear screen
#        os.system( [ 'clear', 'cls' ][ os.name == 'nt' ] )
#        self.logger.debug(u"{0}!".format(self.game_name))
#        self.logger.debug("Round: " + str(self.round))

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

        if self.finished:
            self.logger.debug("Game Over!")
            if self.winner != None:
                self.logger.debug(str(self.winner.name) + " is the winner")
            else:
                self.logger.debug("Game was a draw")
                
