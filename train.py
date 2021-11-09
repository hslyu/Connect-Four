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
import pickle

def main():
    """ Play a game!
    """
    
    stats = [0, 0, 0] # [p1 wins, p2 wins, ties]
    avg_reward = 0
    num_update = 0

    g = Game(verbose=False)
#    g = Game(verbose=True)
#    g.print_state()
    player1 = g.players[0] # Q
    player2 = g.players[1]
    
    
    exit = False
    while True:
        while not g.finished:
#            time.sleep(.6)
            g.next_move()
        
        g.find_streak()
#        g.print_state(stats)
        
        if g.winner == None:
            stats[2] += 1
        
        elif g.winner == player1:
            stats[0] += 1
            
        elif g.winner == player2:
            stats[1] += 1
        
        avg_reward += player1.sum_reward
        player1.reset()
        g.new_game()
#        g.print_state(stats)
        if player1.is_updatable():
            player1.update()
            player1.save()
#            for i in range(5):
#                print(f'Q table is updated {num_update = }')
            num_update += 1
#            time.sleep(.5)

        if (sum(stats)+1) % 100 == 0:
            save_file(stats, 'data/stats.pkl')
            save_file(avg_reward/100, 'data/avg_reward.pkl')
            print_status(player1, player2, stats, avg_reward, num_update)
            avg_reward = 0 # reset avg reward
            
def save_file(variable, path):
    with open(path, 'wb') as f:
        pickle.dump(variable, f)

def print_status(player1, player2, stats, avg_reward, num_update):
    print(f'{player1.name}: {stats[0]},\t {player2.name}: {stats[1]},\t\t\t ties : {stats[2]} , \t{avg_reward = }, \t{num_update =}')
        
if __name__ == "__main__": # Default "main method" idiom.
    main()
