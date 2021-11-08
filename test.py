import numpy as np
h = 3
w = 2
board = []
for i in range(h):
    board.append([])
    for j in range(w):
        board[i].append(' ')

#print(f'{len(board)=}')
#print(f'{len(board[0])=}')
#
#board[0][1]='a'
#print(board[0])
#print(np.argwhere(np.array(board[0]) == ' ').ravel())

def parent(a):
    def child_fn():
        return a+1
    return child_fn

a=3
child=parent(a)
print(child())
a+=1
print(child())
