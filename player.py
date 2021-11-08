import cfg
from minimax import Minimax
import numpy as np
import copy

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
                 board_height = HEIGHT, board_width = WIDTH, epsilon = 0.1):
        self.type = "QPlayer"
        self.name = name
        self.color = color
        self.board_width = WIDTH
        self.board_height = HEIGHT
        self.epsilon = epsilon
        self.Q = {}
        self.count = {}
        self.discount_factor = discount_factor

    def __str__(self):
        return "Q learning player"

    def move(self, board):
        
        action = self._move(board)
        reward = self.calc_reward(board, action)
        print(f'{reward}')
        next_board = self.calc_next_board(board, action)
        
        # board is list, so it is unhashable
        # tuple is hashable
        state = self._get_board_key(board)
        next_state = self._get_board_key(next_board)

        if state not in self.Q.keys():
            self.Q[state] = {}
            for a in self.available_actions(board):
                self.Q[state][a] = 0
        if state not in self.count.keys():
            self.count[state] = 0            
        if next_state not in self.Q.keys():
            self.Q[state] = {}
            for a in self.available_actions(next_board):
                self.Q[state][a] = 0

        next_state, state, 
        if next_state in self.Q.keys():
            try:
                self.count[state] += 1
                # next_board가 key에 있으면, _move에서 action이 계산된 적 있다
                best_next_action = np.argmax(self.Q[next_state])
                delta = self.calc_reward(board, action) + \
                            self.discount_factor*self.Q[next_state][best_next_action] - self.Q[state][action]
                self.Q[state][action] += delta/self.count[state]
            except KeyError:
                print(f'{action = }')
                print(f'{best_next_action = }')
                print(f'{self.Q[state] = }')
                print(f'{self.Q[next_state] = }')
                
        else:
            self.count[state] = 1
            actions = self.available_actions(next_board)
            self.Q[next_state] = {}
            for column in actions:
                self.Q[next_state][column] = 0
            self.Q[state][action] += self.calc_reward(board, action)/self.count[state]

        return action

    def calc_next_board(self, board, action):
        """
        returns next state if given board and action(chosen column)
        """
        next_board = copy.deepcopy(board)
        for i in range(self.board_height):
            if board[i][action] == ' ':
                next_board[i][action] = self.color
                break
        return next_board
    
    def calc_reward(self, board, action):
        """
        Calculate difference of the good positions between board and next board
        
        Params:
            board (list) : connect4 board, board[0] = highest row
            action (int) : chosen column
        """
        def _calc_reward(board):
            reward = 0
            for row in range(self.board_height):
                for col in range(self.board_width):
                    if board[row][col] != self.color:
                        continue
                    reward += check_up(board, row, col)
                    reward += check_right(board, row, col)
                    reward += check_vertical_up(board, row, col)
                    reward += check_vertical_down(board, row, col)
            return reward
                    

        # →, ↑, ↗, ↘ 만 체크해도 보드 전체를 스캔하기 때문에 각각의 반대방향을 고려하게됨{{{
        def check_up(board, row, col):
            counter = 0
            i = 0
            while True:
                # row - i eqauls to "goes up i rows"
                # 0 : highest row index 
                if board[row-i][col] == self.color:
                    counter += 1
                elif board[row-i][col] == ' ':
                    continue
                else:
                    return 0

                # break if row-i is highest row (0)
                if row - i <= 0:
                    break
                i += 1
            if counter >= STREAK:
                return 1e8
            return counter*2

        def check_right(board, row, col):
            counter = 0
            i = 0
            while True:
                if board[row][col+i] == self.color:
                    counter += 1
                elif board[row][col+i] == ' ':
                    continue
                else:
                    return 0
                
                # break if col+i is last column
                if col + i <= self.board_width-1:
                    break
                i += 1

            if counter >= STREAK:
                return 1e8
            return counter*2

        def check_vertical_down(board, row, col):
            counter = 0
            i = 0
            while True:
                if board[row+i][col+i] == self.color:
                    counter += 1
                elif board[row+i][col+i] == ' ':
                    continue
                else:
                    return 0

                if col + i <= self.board_width-1 or row + i <=self.board_height-1:
                    break
                i+=1
            if counter >= STREAK:
                return 1e8
            return counter*2

        def check_vertical_up(board, row, col):
            counter = 0
            i = 0
            while True:
                if board[row-i][col+i] == self.color:
                    counter += 1
                elif board[row-i][col+i] == ' ':
                    continue
                else:
                    return 0

                if col + i <= self.board_width-1 or row - i <=self.board_height-1:
                    break
                i+=1
            if counter >= STREAK:
                return 1e8
            return counter*2#}}}
                    
        next_board = self.calc_next_board(board, action)
        return _calc_reward(next_board) - _calc_reward(board)
    
    def _get_board_key(self, board):
        return np.array(board).tobytes()
    
    
    def _move(self, board):
        # report : number of actions varies with the state

        # If some columns are full, we cannot put at full column
        actions = self.available_actions(board)
        print(f'available {actions=}')

        state = self._get_board_key(board)
        # if there's no updated Q values, register key "board" in Q
        print(f'{state not in self.Q.keys() = }')
        if state not in self.Q.keys() or np.random.random() < self.epsilon:
            print('Epsilon policy')
            print('Epsilon policy')
            print('Epsilon policy')
            chosen_action_index = np.random.choice(actions)
            print(f'{actions =}')
            print(f'{chosen_action_index = }')
        else:
            print('Greedy policy')
            print('Greedy policy')
            print('Greedy policy')
            Q_max = -1e20
            for action in self.Q[state].keys():
                if self.Q[state][action] > Q_max:
                    Q_max = self.Q[state][action] 
                    best_index = action
            print(f'{best_index}')
            tie = [k for k in self.Q[state].keys() if self.Q[state][k] == self.Q[state][best_index]]
            print(f'{tie=}')
            chosen_action_index = np.random.choice(tie)
            print(f'{chosen_action_index = }')

        return chosen_action_index


    def available_actions(self, board):
        '''
        board[0] is highest row
        params
            board : 2D array representing connect4 board
        return
            (numpy array) : index of columns that are not full.
        '''
        return np.argwhere(np.array(board[-1]) == ' ').ravel()

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
        
        m = Minimax(board, self.color)
        best_move, value = m.bestMove(self.difficulty, board, self.color)
        return best_move

def main():
    player = QPlayer('','o', epsilon=1)
    board = []
    for i in range(HEIGHT):
        board.append([])
        for j in range(WIDTH):
            board[i].append(' ')
    print(player._move(board))
    while True:
        action = player.move(board)
        print(f'{action=}')
        board = player.calc_next_board(board, action)
        print_board(board)
        a = input("enter anything to proceed")
        

if __name__ == "__main__":
    main()
