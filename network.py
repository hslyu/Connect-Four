import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class DQN(nn.Module):
    def __init__(self, h, w, outputs):
        super(DQN, self).__init__()
        self.conv1 = nn.Conv2d(1, 81, kernel_size = 2)
        self.conv2 = nn.Conv2d(81, 32, kernel_size = 1)
        self.conv3 = nn.Conv2d(32, 256, kernel_size = 2)

        def conv2d_size_out(size, kernel_size = 2, stride = 1):
            return (size - kernel_size)//stride + 1

        convh = conv2d_size_out(conv2d_size_out(h))
        convw = conv2d_size_out(conv2d_size_out(w))
        linear_input_size = convh*convw*256
        self.fc7 = nn.Linear(linear_input_size, linear_input_size//4, bias=True)
        self.fc8 = nn.Linear(linear_input_size//4, linear_input_size//4, bias=True)
        self.fc9 = nn.Linear(linear_input_size//4, linear_input_size//8, bias=True)
        self.fc10 = nn.Linear(linear_input_size//8, linear_input_size//8, bias=True)
        self.fc11 = nn.Linear(linear_input_size//8, linear_input_size//8, bias=True)
        self.fc12 = nn.Linear(linear_input_size//8, linear_input_size//16, bias=True)
        self.fc13 = nn.Linear(linear_input_size//16, outputs)

    def forward(self, x):
        x = x.to(device).float()
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        # Flatten
        x = x.view(x.size(0),-1)
        x = F.relu(self.fc7(x))
        x = F.relu(self.fc8(x))
        x = F.relu(self.fc9(x))
        residual = x
        x = F.relu(self.fc10(x))
        x = F.relu(self.fc11(x)+residual)
        x = F.relu(self.fc12(x))
        return self.fc13(x)

if __name__ == "__main__":
    import numpy as np
    from board import *
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    device = torch.device("cpu")

    n = DQN(3,5,5)
    board = np.random.randint(2, size=(3,1,3,5))
#    am = torch.cat([available_moves(b.reshape((3,5))).tolist() for b in board])
    am = [available_moves(b.reshape(3,5),True) for b in board]
    print(board)
    print(f'{am = }')
    t=n(torch.from_numpy(board))[0]
    print('-----')
    print('-----')
    print(f'{n(torch.from_numpy(board)) = }')
    b = torch.tensor([t[am[i]].sort(descending=True).values[0] for i,t in enumerate(n(torch.from_numpy(board)))])
    print('-----')
    print('-----')
    print(b)
    print('-----')
    print('-----')
    for i,t in enumerate(n(torch.from_numpy(board))):
        print(t[am[i]].sort()[-1])
        print('-----')

#    print(f'{n(torch.from_numpy(board)) = }\n')
#    print(f'{n(torch.from_numpy(board))[[True, True, False, False, False]] = }\n')
#    print(f'{n(torch.from_numpy(board)).sort(descending=True).indices.tolist() = }\n')
#    print(f'{n(torch.from_numpy(board)) = }\n')
#    print(f'{n(torch.from_numpy(board)).max(1) = }\n')
#    print(f'{n(torch.from_numpy(board)).max(1)[1] = }\n')
#    print(f'{n(torch.from_numpy(board)).max(1)[1].item() =}\n')
