from connect4 import *
import time
import pickle
from datetime import datetime
from player import *

def main():
    # set game
    g = Game(verbose=False)
    diff = 1
    player1 = QPlayer("Q-agent", g.colors[0] , batch_size=5e3, epsilon=.1, epsilon_min=0.0, epsilon_decay=0.9999)
    player1.load('11-12-22:15_small_board_')
#    print(len(player1.Q))
    player2 = MiniMaxPlayer("Minimax", g.colors[1], diff+1)
    g.set_player(player1, player2)
    
    # set game information 
    stats = [0, 0, 0] # [p1 wins, p2 wins, ties]
    avg_reward = 0
    num_update = 11665
    avg_reward_list = []
    stats_list = []

    now = datetime.now()
    filecode = now.strftime("%m-%d-%H:%M")

    # Repeat game
    while True:
       
        # Repeat game's turn
        while True:
#            a=input("Q player turn, enter to proceed")
            # Q 플레이어의 움직임은 끝나야 관측함
            # Q player's move
            g.play_round()
            # If finish, observe
            if g.finished:
                g.players[0].observe(g.board, g.finished, g.winner)
                break
#            a=input("M player turn, enter to proceed")
            # M 플레이어의 움직임은 무조건 관측함
            # M player's move
            g.play_round()
            g.players[0].observe(g.board, g.finished, g.winner)
            if g.finished:
                break
        
        g.find_streak()
#        g.print_state(stats)
        
        if g.winner == player1:
            stats[0] += 1
        elif g.winner == player2:
            stats[1] += 1
        else:
            stats[2] += 1
        
        avg_reward += player1.sum_reward
        player1.reset()
        g.new_game()

#        g.print_state(stats)
        if player1.is_updatable():
            player1.update()
            save_file(player1.Q, f'data/{filecode}_small_board_Q.pkl')
            save_file(player1.epsilon, f'data/{filecode}_small_board_epsilon.pkl')
            save_file(player1.count, f'data/{filecode}_small_board_count.pkl')
            num_update += 1

        if sum(stats) == 1000:
            avg_reward_list.append(avg_reward/1000)
            stats_list.append(stats)

            save_file(stats_list, f'data/{filecode}_small_board_stats.pkl')
            save_file(avg_reward_list, f'data/{filecode}_small_board_avg_reward.pkl')

            print_status(player1, player2, stats, avg_reward_list[-1], num_update)
            avg_reward = 0 # reset avg reward
            stats = [0,0,0]
            
def save_file(variable, path):
    with open(path, 'wb') as f:
        pickle.dump(variable, f)

def print_status(player1, player2, stats, avg_reward, num_update):
    print(f'{player1.name}: {stats[0]}, {player2.name}: {stats[1]}, ties : {stats[2]} , {avg_reward=:.2f}, {num_update =}, epsilon = {player1.epsilon:.5f}')
        
if __name__ == "__main__": # Default "main method" idiom.
    main()
