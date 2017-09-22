#!/usr/bin/env python3
import sys
import numpy as np
import math

from matplotlib import pyplot as plt
from copy import deepcopy
from random import randint,seed

'''
opt = [up,right,down,left]
'''

'''
Solvable if N is odd and inversions are even
if N is even and blanc is on even row from bottom and inversion is odd
if N is even and blanc is on odd row from bottom and inversion is even
inversion of (a,b) if a appears before b but a > b
'''


class Puzzle:
    directions = np.array([[-1,0],[0,1],[1,0],[0,-1]])
    def __init__(self,N,board=np.arange(N*N)):
        self.N = N
        self.g = 0
        self.board = board
        np.random.shuffle(temp)
        self.board = temp.reshape(N,N)                  # Randomly shuffle board
        self.ind_0 = np.where(self.board==0)            # Indices of blank space
        self.x = np.roll(np.repeat(np.arange(N),N),1)   # Blank is last. Index in the solution of the numbers
        self.y = np.tile(np.roll(np.arange(N),1),N)     # Blank, i.e. 0, is last
        self.solution = np.roll(np.arange(N*N),N*N-1).reshape((N,N)) # Can also be made by np.zeros((N,N)) and use self.x(y) and arange
        self.h = self.heuristic()
        self.opt = self.options()
        self.isSolvable()


    def heuristic(self):#,board_temp,ind_0):
        #bool_mat = board_temp!=self.solution
        bool_mat = self.board!=self.solution
        bool_mat[self.ind_0[0],self.ind_0[1]] = False
#        values = board_temp[bool_mat].flatten()
        values = self.board[bool_mat].flatten()
        x,y = np.where(bool_mat)
        x_ = self.x[values]-x
        y_ = self.y[values]-y
        return np.sum(np.abs(x_))+np.sum(np.abs(y_))+self.g
    def options(self):
        out = np.ones(4)
        if (not self.ind_0[0]%(self.N-1)) and (not self.ind_0[1]%(self.N-1)):
            if [self.ind_0[0],self.ind_0[1]] == [0,0]:
                return np.array([0,1,1,0])
            elif [self.ind_0[0],self.ind_0[1]] == [0,self.N-1]:
                return np.array([0,0,1,1])
            elif [self.ind_0[0],self.ind_0[1]] == [self.N-1,self.N-1]:
                return np.array([1,0,0,1])
            elif [self.ind_0[0],self.ind_0[1]] == [self.N-1,0]:
                return np.array([1,1,0,0])
            else:
                print('Something went wrong in self.options()'),exit()
        elif (not self.ind_0[0]%(self.N-1)) or (not self.ind_0[1]%(self.N-1)):
            if self.ind_0[0] == 0:
                return np.array([0,1,1,1])
            elif self.ind_0[0] == self.N-1:
                return np.array([1,1,0,1])
            elif self.ind_0[1] == 0:
                return np.array([1,1,1,0])
            elif self.ind_0[1] == self.N-1:
                return np.array([1,0,1,1])
            else:
                print('Something went wrong in self.options()'),exit()
        else:
            return np.array([1,1,1,1])
    def update_ind_0(self):
        self.ind_0 = np.where(self.board==0)
    def update_g(self):
        self.g = self.g+1
    def update_opt(self):
        self.opt = self.options()
    def update_h(self):
        self.h = self.heuristic()
    def isSolvable(self):
        inv_counter = 0
        values = np.delete(self.board.flatten(),self.ind_0[0]*self.N+self.ind_0[1])
        for i,j in enumerate(values):
            k = 0
            while(np.any(values[0:i-k]>j) and k < i):
                k = k + 1
                values[i-k+1] = values[i-k]
                values[i-k] = j
                inv_counter = inv_counter + 1
        if (self.N%2==1 or self.ind_0[0]%2==1) and inv_counter%2 == 0:
            print('Board is solvable! With h = {}'.format(self.h))
            self.soft_print()
        elif (self.N%2==0 and self.ind_0[0]%2==0) and inv_counter%2==1:
            print('Board is solvable! With h = {}'.format(self.h))
            self.soft_print()
        else:
            print('Board is not solvable! Number of inversions = {}'.format(inv_counter))
            self.soft_print()
            exit()

    def soft_print(self,option=False):
        plot_mat = self.board
        if option:
            plot_mat = self.solution
        print('\n-------------------------')
        print('\t h = ',self.h)
        for i in range(self.N):
            print('\t',plot_mat[i,0:self.N])
        print('-------------------------')

    def print_board(self,option=False):
        plot_mat = self.board
        if option:
            plot_mat = self.solution
        fig, ax = plt.subplots()
 #       ax.matshow(self.board,cmap=)
        for (i,j),k in np.ndenumerate(plot_mat):
            ax.text(i+0.5,j+0.5,k,ha='center',va='center')
        ax.set_xlim(0,self.N)
        ax.set_ylim(0,self.N)
        ax.set_xticks(np.arange(self.N))
        ax.set_yticks(np.arange(self.N))
#        ax.set_axis_off()
        ax.grid()
#        plt.imshow(self.board)
        plt.show()

class Solver:
    '''
    Need an OPEN variable to keep track of open nodes
    Need a CLOSED variable to keep track of the closed nodes
    These needs to be ordered according to the cost function
    '''

    def __init__(self,board_init):
        self.Puzz = deepcopy(board_init)
        self.CLOSED = []
        self.OPEN = [deepcopy(board_init)]
     #   self.Puzz.soft_print()
     #   print(self.Puzz.h)
        self.moves = []
        self.options = [deepcopy(board_init) for i in range(np.sum(self.Puzz.opt))]
        self.swap()
        self.h_list = np.array([i.heuristic() for i in self.options])
        self.solve()
    def swap(self):
        for i in range(len(self.options)):
            way = self.Puzz.directions[self.Puzz.opt==1][i]
            self.options[i].board[self.Puzz.ind_0[0],self.Puzz.ind_0[1]] = self.Puzz.board[self.Puzz.ind_0[0]+way[0],self.Puzz.ind_0[1]+way[1]]
            self.options[i].board[self.Puzz.ind_0[0]+way[0],self.Puzz.ind_0[1]+way[1]]=0
            self.options[i].update_ind_0()
            self.options[i].update_g()
            self.options[i].update_opt()
            self.options[i].update_h()
    def solve(self):
        while bool(len(self.OPEN)):
            current = OPEN[0]
 #           print(self.h_list)
 #           print(self.h_list.argmin())
            nodes=self.h_list == self.h_list[self.h_list.argmin()]
            print(nodes)
            ind_temp = np.arange(len(nodes))[nodes][0]
            if self.options[ind_temp].g == 1 or self.options[ind_temp].g==3:
                ind_temp = np.arange(len(nodes))[nodes][1]
            if self.options[ind_temp].g == 5:
                print(ind_temp, nodes,self.h_list),exit()
            print(ind_temp)
            if self.options[ind_temp].g > 9:
                print('OK')
                exit()
            b = Solver(self.options[ind_temp])
            
            exit()

#np.random.seed(85854)
#np.random.seed(85821)
#seedNr=randint(0,99999)
#print(seedNr)
#np.random.seed(seedNr)
np.random.seed(61590)
a = Puzzle(3)
#a.soft_print()
#a.soft_print(option=True)
#print(a.h),exit()
#a.print_board()
#a.print_board(option=True)
#print(a.opt)
b = Solver(a)
#b.options[0].soft_print()
#b.options[1].soft_print()
#b.options[2].soft_print()
#b.options[3].soft_print()
#print(b.options[0].opt)
#print(b.options[0].ind_0)

exit()

