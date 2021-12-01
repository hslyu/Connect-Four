import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class DQN(nn.Module):
    def __init__(self, h, w, outputs):
        super(DQN, self).__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size = 3)

        def conv2d_size_out(size, kernel_size = 3, stride = 1):
            return (size - kernel_size)//stride + 1

        convh = conv2d_size_out(h)
        convw = conv2d_size_out(w)
        linear_input_size = convh*convw*16
        self.fc1 = nn.Linear(linear_input_size, linear_input_size)
        self.fc2 = nn.Linear(linear_input_size, outputs)

    def forward(self, x):
        x = x.to(device)
        x = F.relu(self.conv1(x))
        x = F.relu(self.fc1(x.view(x.size(0),-1)))
        return self.fc2(x)

if __name__ == "__main__":
    import numpy as np
    n = DQN(3,5,5)
    board = np.zeros((1,3,5))
    n.forward(torch.from_numpy(board).unsqueeze(0))
