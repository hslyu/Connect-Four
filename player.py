import cfg
from minimax import Minimax
from memory import ReplayBuffer
from board import *

import numpy as np
import random
import copy
import pickle
from collections import namedtuple

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T
import network

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
    def __init__(self, name, color, board_width = cfg.WIDTH):
        self.type = "Human"
        self.name = name
        self.color = color
        self.board_width = cfg.WIDTH
    
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

class DQNPlayer(Player):
    def __init__(self, name, color, streak=cfg.STREAK,
                epsilon=1, epsilon_min=0, epsilon_decay=1, 
                batch_size=5e3, gamma = 0.95, lr=0.003):
        self.name = name
        self.color = color
        self.opp_color = -1 if color == 1 else 1
        self.streak = streak
        self.sum_reward = 0

        # Hyperparameter
        self.steps = 0 
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay 
        self.gamma = gamma

        # replay buffer
        self.transition_counter = 0
        self.batch_size = batch_size
        self.buffer = ReplayBuffer(5e5, 1)

        # Network
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.policy_net = network.DQN(cfg.HEIGHT, cfg.WIDTH, cfg.WIDTH).to(self.device)
        self.target_net = network.DQN(cfg.HEIGHT, cfg.WIDTH, cfg.WIDTH).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
#        self.optimizer = optim.RMSprop(self.policy_net.parameters(), lr)
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr)
#        self.optimizer = optim.SGD(self.policy_net.parameters(), lr)

    def __str__(self):
        return "DQN player"

    def move(self, board):
        self.board = copy.deepcopy(board)

        if random.random() > self.epsilon:
            with torch.no_grad():
                # reshape for add C for CHW
                # unsqueeze for add batch dimension B for BCHW
                state = torch.from_numpy(np.array(board).reshape((1,1,3,5)))
                actions = self.policy_net(state).sort(descending=True).indices.tolist()[0]
                for action in actions:
                    if action in available_moves(board):
                        self.action = action
                        return action
        else:
            while True:
                action = random.randrange(5)
                if action in available_moves(board):
                    self.action = action
                    return action

        return None

    def observe(self, next_board, done, winner):
        board = self.board
        action = self.action

        reward = self.calc_reward(board, next_board, done, winner)
        # For averaging
        self.sum_reward += reward

        #Todo: define transition
        #Todo: seperate update and move
        state = np.array(board).reshape((1,3,5))
        next_state = np.array(next_board).reshape((1,3,5))
        self.buffer.push(state, action, next_state, reward, done)
        self.transition_counter += 1

    def calc_reward(self, board, next_board, done, winner):
        if done and winner == self:
            return 1
        elif done and (winner == None):
            return 0
        elif done and (winner is not None): ## Opponent wins
            return -1

        streak_diffs = [check_streak(next_board, self.color, streak) 
                                        - check_streak(board, self.color, streak) 
                                                    for streak in range(2, self.streak+1)]
        opp_streak_diffs = [check_streak(next_board, self.opp_color, streak) 
                                        - check_streak(board, self.opp_color, streak) 
                                                    for streak in range(2, self.streak+1)]
#        print(f'{streak_diffs = }')
#        print(f'{opp_streak_diffs = }')

        reward = 0
        for i,v in enumerate(streak_diffs):
            reward += v*25**(i+1)/50

        for i,v in enumerate(opp_streak_diffs):
            reward -= v*20**(i+1)/50

        return reward

    def is_updatable(self):
        return self.transition_counter >= self.batch_size

    def update(self):
        Transition = namedtuple('Transition', 
                                ('state', 'action', 'next_state', 'reward', 'done'))

        if len(self.buffer) < self.batch_size:
            return
        transitions = self.buffer.sample_batch(self.batch_size)
        batch = Transition(*zip(*transitions))
        state_batch = torch.tensor(np.array(batch.state)).to(self.device)
        action_batch = torch.tensor(np.array(batch.action)).to(self.device)
        reward_batch = torch.tensor(np.array(batch.reward)).to(self.device)
        done_batch = torch.tensor(np.array(batch.done)).to(self.device)

        non_final_next_states = torch.tensor(np.array([s for done, s in zip(batch.done, batch.next_state) if done == False])).to(self.device)

        state_action_values = self.policy_net(state_batch).gather(1, action_batch.unsqueeze(1))
        next_state_values = torch.zeros(int(self.batch_size), device=self.device)

        am = [available_moves(s.reshape(3,5), boolean=True) for done, s in zip(batch.done, batch.next_state) if done == False]
        next_state_values[~done_batch] = torch.tensor(
                                                [qsa[am[i]].sort(descending=True).values[0] for i, qsa in enumerate(self.target_net(non_final_next_states))]).to(self.device)
        expected_state_action_values = (next_state_values * self.gamma) + reward_batch

        #
        criterion = nn.SmoothL1Loss()
        loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))
#        print(state_action_values)
#        print(expected_state_action_values.unsqueeze(1))

        #
        self.optimizer.zero_grad()
        loss.backward()
        for param in self.policy_net.parameters():
            param.grad.data.clamp_(-1, 1)
        self.optimizer.step()

        if self.epsilon >= self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        self.transition_counter = 0 

        return loss.item()


    def reset(self):
        self.sum_reward = 0 

    def soft_update(self, tau):
        for target_param, policy_param in zip(self.target_net.parameters(), self.policy_net.parameters()):
            target_param.data.copy_(tau*policy_param.data + (1.0-tau)*target_param.data)

class QPlayer(Player):
    """ Player object.  This class is for human players.
    """
    
    type = None # possible types are "Human" and "AI"
    name = None
    color = None
    Q = None # Q function dictionary. Q = {}, 
             # Q[board] = np.array with size self.available_actions(board)
    def __init__(self, name, color, discount_factor = 0.99,
                 streak = cfg.STREAK, height = cfg.HEIGHT, width = cfg.WIDTH, 
                 epsilon = 1, epsilon_min = 0.03, epsilon_decay=0.999, batch_size=5e3):
        self.type = "QPlayer"
        self.name = name
        self.color = color
        self.opp_color = -1 if color == 1 else 1
        self.streak = streak
        self.width = width
        self.height = height
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.epsilon = epsilon
        self.Q = {}
        self.count = {}
        self.board = []
        self.action = None
        self.discount_factor = discount_factor

        self.buffer = ReplayBuffer(1e6, 1)
        self.batch_size = batch_size
        self.transition_counter = 0

        self.sum_reward = 0

    def move(self, board):
        # report : number of actions varies with the state

        # If some columns are full, we cannot put at full column
        actions = available_moves(board)

        state = self._get_key_from_board(board)
        # if there's no updated Q values, register key "board" in Q
        if state not in self.Q.keys() or np.random.random() < self.epsilon:
            chosen_action_index = np.random.choice(actions)
        else:
            Q_max = -999999
            for action in self.Q[state].keys():
                if self.Q[state][action] > Q_max:
                    Q_max = self.Q[state][action] 
                    best_index = action
            tie = [k for k in self.Q[state].keys() if self.Q[state][k] == self.Q[state][best_index]]
            chosen_action_index = np.random.choice(tie)

        self.board = copy.deepcopy(board)
        self.action = chosen_action_index
        return chosen_action_index

    # step function
    def observe(self, next_board, done, winner):
        board = self.board
        action = self.action

        reward = self.calc_reward(board, next_board, done, winner)
        self.sum_reward += reward

#        for row in board:
#            print(row)
#        print(f'{action =}')
#        for row in next_board:
#            print(row)
#        print(f'{reward = }')
#        print(f'{done = }')
#        print(f'{winner = }')


        # board is list, so it is unhashable
        # tuple is hashable
        state = self._get_key_from_board(board)
        next_state = self._get_key_from_board(next_board)

        #Todo: define transition
        #Todo: seperate update and move
        self.buffer.push(state, action, next_state, reward, done)
        self.transition_counter += 1
        return action

    def calc_reward(self, board, next_board, done, winner):
        if done and winner == self:
            return 1
        elif done and (winner == None):
            return 0
        elif done and (winner is not None): ## Opponent wins
            return -1

        streak_diffs = [check_streak(next_board, self.color, streak) 
                                        - check_streak(board, self.color, streak) 
                                                    for streak in range(2, self.streak+1)]
        opp_streak_diffs = [check_streak(next_board, self.opp_color, streak) 
                                        - check_streak(board, self.opp_color, streak) 
                                                    for streak in range(2, self.streak+1)]
#        print(f'{streak_diffs = }')
#        print(f'{opp_streak_diffs = }')

        reward = 0
        for i,v in enumerate(streak_diffs):
            reward += v*25**(i+1)/50

        for i,v in enumerate(opp_streak_diffs):
            reward -= v*20**(i+1)/50

        return reward
    
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
            if self.Q[next_state] == {}:
                max_next_q = 0
            else:
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

        if self.epsilon >= self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        self.transition_counter = 0

    def _get_key_from_board(self, board):
        return np.array(board).tobytes()

    def _get_board_from_key(self, key):
        np_array = np.frombuffer(key, dtype='int64')
        np_array = np_array.reshape((self.height, self.width))
        return np_array.tolist()
    
    def reset(self):
        self.sum_reward = 0

    def __str__(self):
        return "Q learning player"

    def save(self):
        with open('data/Q.pkl', 'wb') as f:
            pickle.dump(self.Q, f)
        with open('data/epsilon.pkl', 'wb') as f:
            pickle.dump(self.epsilon, f)

    def load(self, filecode):
        with open(f'data/{filecode}Q.pkl', 'rb') as f:
            self.Q = pickle.load(f)
#        with open('data/epsilon.pkl', 'rb') as f:
#            self.epsilon = pickle.load(f)

    def __repr__(self):
        return "Q learning player"


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

    def __repr__(self):
        return "Minimax Player"

def main():
#    player = DQNPlayer('',1, epsilon=0)
    player = QPlayer('',1, epsilon=0)
    board = []
    for i in range(cfg.HEIGHT):
        board.append([])
        for j in range(cfg.WIDTH):
            board[i].append(random.randint(0,1))

    while len(available_moves(board)) > 0:
        action = player.move(board)
        print(f'{action=}')
        board = calc_next_board(board, action, player.color)
        print_board(board)
        a = input("enter anything to proceed")
        

if __name__ == "__main__":
    main()
    
