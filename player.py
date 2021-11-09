import cfg
from minimax import Minimax
import numpy as np
import copy
import pickle
from memory import ReplayBuffer
from board import *

WIDTH = cfg.WIDTH
HEIGHT = cfg.HEIGHT
STREAK = cfg.STREAK

def print_board(board):
    for row in board:
        print(row)

class Player:
    def __str__(self):
        return "Generic player"
    
    def move(self, board):
        return 0

class HumanPlayer(Player):
    """ Player object.  This class is for human players.
    """
    
    type = None # possible types are "Human" and "AI"
    name = None
    color = None
    def __init__(self, name, color, board_width = WIDTH):
        self.type = "Human"
        self.name = name
        self.color = color
        self.board_width = WIDTH
    
    def move(self, board):
        #print("{0}'s turn.  {0} is {1}".format(self.name, self.color))
        column = None
        while column == None:
            try:
                choice = int(input("Enter a move (by column number): ")) - 1
            except ValueError:
                choice = None
            if 0 <= choice <= self.board_width:
                column = choice
            else:
                print("Invalid choice, try again")
        return column

class QPlayer(Player):
    """ Player object.  This class is for human players.
    """
    
    type = None # possible types are "Human" and "AI"
    name = None
    color = None
    Q = None # Q function dictionary. Q = {}, 
             # Q[board] = np.array with size self.available_actions(board)
    def __init__(self, name, color, discount_factor = 0.99,
                 streak = STREAK, height = HEIGHT, width = WIDTH, 
                 epsilon = 0.1, epsilon_min = 0.01, epsilon_decay=0.995, batch_size=1e3):
        self.type = "QPlayer"
        self.name = name
        self.color = color
        self.opp_color = 'x' if color == 'o' else 'o'
        self.streak = streak
        self.width = width
        self.height = height
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.epsilon = epsilon
        self.Q = {}
        self.count = {}
        self.discount_factor = discount_factor

        self.buffer = ReplayBuffer(1e5, 1)
        self.batch_size = batch_size
        self.transition_counter = 0

        self.sum_reward = 0

    def reset(self):
        self.sum_reward = 0

    def __str__(self):
        return "Q learning player"

    def save(self):
        with open('data/Q.pkl', 'wb') as f:
            pickle.dump(self.Q, f)
        with open('data/epsilon.pkl', 'wb') as f:
            pickle.dump(self.epsilon, f)

    def load(self):
        with open('data/Q.pkl', 'rb') as f:
            self.Q = pickle.load(f)
        with open('data/epsilon.pkl', 'rb') as f:
            self.epsilon = pickle.load(f)

    def move(self, board):
        action = self._move(board)
        reward = self.calc_reward(board, action)
        self.sum_reward += reward
        done, result = self.calc_done(board, action)
        next_board = calc_next_board(board, action, self.color)
        # board is list, so it is unhashable
        # tuple is hashable
        state = self._get_key_from_board(board)
        next_state = self._get_key_from_board(next_board)

        #Todo: define transition
        #Todo: seperate update and move
        self.buffer.push(state,action,next_state,reward,done)
        self.transition_counter += 1
        return action

    def calc_reward(self, board, action):
        done, result = self.calc_done(board, action)
        if done and result == 'winner':
            return 1e10
        elif done and result == 'loser':
            return -1e10
        elif done and result =='tie':
            return -1e3

        m = Minimax(self.opp_color)
        next_board = calc_next_board(board, action, self.color)
        opp_best_move, opp_value = m.best_move(2, next_board, self.opp_color)

        reward = -opp_value
        return reward
    
    def calc_done(self, board, action):
        """
        Return:
            done, isWinner (bool, {bool, None}): whether this game is finished,
                                                 whether the Q player wins, loses, and ties.
        """
        next_board = calc_next_board(board, action, self.color)
        if check_streak(next_board, self.color, self.streak) > 0:
            return True, "win"
        elif check_streak(next_board, self.opp_color, self.streak) > 0:
            return True, "lose"
        elif not np.any(np.array(board[-1]) == ' '):
            return True, "tie"

        return False, "ongoing"

    def is_updatable(self):
        return self.transition_counter >= self.batch_size
        
    def update(self):
        batch = self.buffer.sample_batch(self.batch_size)
        for sample in batch:
            state = sample.state
            action = sample.action
            next_state = sample.next_state
            reward = sample.reward 
            done = sample.done
            board = self._get_board_from_key(state)
            next_board = self._get_board_from_key(next_state)

            if state not in self.Q.keys():
                self.Q[state] = {}
                for a in available_moves(board):
                    self.Q[state][a] = 0

            if state not in self.count.keys():
                self.count[state] = 0            

            if next_state not in self.Q.keys():
                self.Q[next_state] = {}
                for a in available_moves(next_board):
                    self.Q[next_state][a] = 0

            self.count[state] += 1
            max_next_q = -1e20
            for action in self.Q[next_state].keys():
                if self.Q[state][action] > max_next_q:
                    max_next_q = self.Q[state][action] 
            try:
                delta = reward + self.discount_factor*max_next_q - self.Q[state][action]
            except KeyError:
                print(f'{available_moves(board) = }')
                print(f'{available_moves(next_board) = }')
                print(f'{best_next_action= }, {action =}')
                exit()
            self.Q[state][action] += delta/self.count[state]
#            print(f'{self.Q[state][action] =}')

        if self.epsilon >= self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            self.transition_counter = 0

    def _get_key_from_board(self, board):
        return np.array(board).tobytes()

    def _get_board_from_key(self, key):
        np_array = np.frombuffer(key, dtype='<U1')
        np_array = np_array.reshape((self.height, self.width))
        return np_array.tolist()
    
    def _move(self, board):
        # report : number of actions varies with the state

        # If some columns are full, we cannot put at full column
        actions = available_moves(board)

        state = self._get_key_from_board(board)
        # if there's no updated Q values, register key "board" in Q
        if state not in self.Q.keys() or np.random.random() < self.epsilon:
            chosen_action_index = np.random.choice(actions)
        else:
            Q_max = -1e20
            for action in self.Q[state].keys():
                if self.Q[state][action] > Q_max:
                    Q_max = self.Q[state][action] 
                    best_index = action
            tie = [k for k in self.Q[state].keys() if self.Q[state][k] == self.Q[state][best_index]]
            chosen_action_index = np.random.choice(tie)

        return chosen_action_index

class MiniMaxPlayer(Player):
    """ MiniMaxPlayer object that extends Player
        The MiniMax algorithm is minimax, the difficulty parameter is the depth to which 
        the search tree is expanded.
    """
    
    difficulty = None
    def __init__(self, name, color, difficulty=5):
        self.type = "MiniMax"
        self.name = name
        self.color = color
        self.difficulty = difficulty
        
    def move(self, board):
        #print("{0}'s turn.  {0} is {1}".format(self.name, self.color))
        
        # sleeping for about 1 second makes it looks like he's thinking
        #time.sleep(random.randrange(8, 17, 1)/10.0)
        #return random.randint(0, 6)
        
        m = Minimax(self.color)
        opt_move, _ = m.best_move(self.difficulty, board, self.color)
        return opt_move

def main():
    player = QPlayer('','o', epsilon=1)
    board = []
    for i in range(HEIGHT):
        board.append([])
        for j in range(WIDTH):
            board[i].append(' ')
    print(f'{player._move(board)}')
    while True:
        action = player.move(board)
        print(f'{action=}')
        board = calc_next_board(board, action, player.color)
        print_board(board)
        a = input("enter anything to proceed")
        

if __name__ == "__main__":
    main()
    
