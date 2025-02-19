# Python Final Project
# Connect Four
#
# Erik Ackermann
# Charlene Wang
#
# Play connect four
# February 27, 2012

from connect4 import *
import time

def main():
    """ Play a game!
    """
    
#    g = Game(verbose=False)
    g = Game(verbose=True)
    g.print_state()
    player1 = g.players[0]
    player2 = g.players[1]
    
    stats = [0, 0, 0] # [p1 wins, p2 wins, ties]
    
    exit = False
    while not exit:
        while not g.finished:
            g.next_move()
#            a = input()
        
        g.find_streak()
        g.print_state()
        
        if g.winner == None:
            stats[2] += 1
        
        elif g.winner == player1:
            stats[0] += 1
            
        elif g.winner == player2:
            stats[1] += 1
        
        print_stats(player1, player2, stats)
        
        time.sleep(.5)
        g.new_game()
        g.print_state()
        
def print_stats(player1, player2, stats):
    print("{0}: {1} wins, {2}: {3} wins, {4} ties".format(player1.name,
        stats[0], player2.name, stats[1], stats[2]))
        
if __name__ == "__main__": # Default "main method" idiom.
    main()
