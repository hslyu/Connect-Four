import torch
import numpy as np

a= torch.FloatTensor(10).uniform_() > .8
print(a)
b=torch.ones(10)
print(torch.ones(10))
b[~a]=0
print(b)

