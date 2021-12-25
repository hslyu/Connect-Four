from connect4 import *
import time

def main():
    # set game
    g = Game(verbose=False)
    diff = 2
    player1 = DQNPlayer("Q-agent", g.colors[0] , epsilon=1, epsilon_decay=1)
    player2 = MiniMaxPlayer("Minimax", g.colors[1], diff+1)
    g.set_player(player1, player2)
    
    # set game information 
    stats = [0, 0, 0] # [p1 wins, p2 wins, ties]
    avg_reward = 0
    num_update = 0
    avg_reward_list = []
    stats_list = []

    # Repeat game
    while True:
       
        # Repeat game's turn
        while True:
            # Q 플레이어의 움직임은 끝나야 관측함
            # Q player's move
            g.play_round()
            # If finish, observe
            if g.finished:
                g.players[0].observe(g.board, g.finished, g.winner)
                break
            g.print_state()
            a=input('enter to proceed')
            # M 플레이어의 움직임은 무조건 관측함
            # M player's move
            g.play_round()
            g.players[0].observe(g.board, g.finished, g.winner)
            if g.finished:
                break
            g.print_state()
            a=input('enter to proceed')

        if g.winner == player1:
            stats[0] += 1
        elif g.winner == player2:
            stats[1] += 1
        else:
            stats[2] += 1
        
#        g.find_streak()
        g.print_state(stats)
        
        
        avg_reward += player1.sum_reward
        player1.reset()
        g.new_game()
#        g.print_state()
        
def print_stats(player1, player2, stats):
    print("{0}: {1} wins, {2}: {3} wins, {4} ties".format(player1.name,
        stats[0], player2.name, stats[1], stats[2]))
        
if __name__ == "__main__": # Default "main method" idiom.
    main()
