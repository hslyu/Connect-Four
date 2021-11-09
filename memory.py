import numpy as np
import random
from collections import namedtuple

Transition = namedtuple('Transition', 
                        ('state', 'action', 'next_state', 'reward', 'done'))

class ReplayBuffer(object):

    def __init__(self, capacity, seed,
                 priority_weight=None, priority_exponent=None,
                 priotirized_experience=False):
        self.capacity = capacity
        self.position = 0
        self.prioritize = priotirized_experience
        self.priority_weight = priority_weight  # Initial importance sampling weight β, annealed to 1 over course of training
        self.priority_exponent = priority_exponent
        if self.prioritize:
            self.memory = []
        else:
            self.memory = []
        # Seed for reproducible results
        np.random.seed(seed)

    def push(self, *args):
        """Saves a transition."""
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        self.memory[self.position] = Transition(*args)
        self.position = int((self.position + 1) % self.capacity)
#        print(f'{self.position = }, {self.memory[-1] = }')

    def sample_batch(self, batch_size):
        return random.sample(self.memory, int(batch_size))

    def __len__(self):
        return len(self.memory)

    def get_buffer_size(self):
        return len(self.memory)

def main():
    test_buffer = ReplayBuffer(1000, 3)

if __name__=='__main__':
    main()
