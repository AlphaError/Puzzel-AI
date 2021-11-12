#!/usr/bin/env python
# coding: utf-8

# Kora S. Hughes - Artificial Intelligence Project 1: 11 Puzzel Problem with A*

""" PROJECT NOTES
“Bramble system” → only 1 tile moves at a time
1 person project

standard:
 -11 tile problem
 -3 X 4 board
"""

import random
import copy
import fileinput
import os

GOAL_BOARD = [0,1,2,3,4,5,6,7,8,9,10,11]  # [[0,1,2,3],[4,5,6,7],[8,9,10,11]], practice goal board
action_translation= {1:"U", 2:"D", 3:"L", 4:"R"}  # output translator
action_translation2= {0:"START", 1:"up", 2:"down", 3:"left", 4:"right"}  # testing helper


class Puzzle:
    '''
    Main Puzzle Class:
    - contains board and helper functions to navigate board
    '''
    # Note: code was made with board dimension versatility in mind but I didnt really feel like testing it base 4x3
    def __init__(self, x=4, y=3):  # init with board dimensions
        assert type(x) == int and type(y) == int
        temp_board = []
        for i in range(y):  # circumvents shallow copy issue with [[0]*x]*y
            temp_row = []
            for i in range(x):
                temp_row.append(0)
            temp_board.append(temp_row)
        self.board = copy.deepcopy(temp_board)  # main board storage
        # stored vars for convenience
        self.size = (x*y) - 1
        self.dimensions = (x, y)

    def __bool__(self):  # validating board
        seen_nums = []
        for y in self.board:  # is valid if all unique nums within size
            for x in y:
                assert type(x) == int
                if x in seen_nums or x < 0 or x > self.size:
                    return False
                else:
                    seen_nums.append(x)
        return True
    
    def __eq__(self, rhs):  # compare the position of all numbers on the board
        # slightly more complex alternative to self.board == rhs.board
        if self.dimensions == rhs.dimensions:
            for i in range(self.dimensions[1]):
                for j in range(self.dimensions[0]):
                    if not self.board[i][j] == rhs.board[i][j]:
                        return False
            return True
        else:
            return False

    def show(self):  # show the board for testing
#         print("*BOARD* " + str(self.size) + "-Puzzle: " + str(self.dimensions))
        p_out = ""
        for y in self.board:
            out = ""
            for x in y:
                out += str(x) + " "
#                 if x < 10:
#                     out += " "
            p_out += out + "\n"
#             print("[ " + out + " ]")
        return p_out

    def flatten(self):  # ended up not using
        ''' helper for testing validity of boards and hashing '''
        lst = []
        for row in self.board:
            for col in row:
                lst.append(col)
        return lst

    def random_fill(self):  # randomizer for board values in testing (before test cases were posted)
        nums = random.sample(range(0, self.size+1), self.size+1)
        # print("adding random board:", nums)
        self.fill(nums)

    def fill(self, vals):  # manually fill puzzle via nested list
        assert len(vals) == self.size+1
        i = 0
        for y in range(0, self.dimensions[1]):
            for x in range(0, self.dimensions[0]):
                # print(vals[i], ":", x, ",", y, ",", i)
                self.board[y][x] = vals[i]
                i += 1
    
    def h(self):
        ''' Manhattan Distance heuristic function for a valid board '''
        ideal_board = Puzzle()
        ideal_board.fill(GOAL_BOARD)  # load the goal state
        # assert bool(self)
        # assert bool(ideal_board)
        h_sum = 0
        for i in range(1, self.size+1):  # get the sum of the differences of every numbers' position
            ideal_coords = ideal_board.get_num(i)  # coordinates of i in the board(s)
            curr_coords = self.get_num(i)
            # make max the two instead of adding for chessboard distance
            value = abs(ideal_coords[0]-curr_coords[0]) + abs(ideal_coords[1]-curr_coords[1])
            h_sum += value
        return h_sum
    
    def action(self, act):
        '''
        takes integer input representing a puzzle move
        edits the present board according to said move
        '''
        assert type(act) == int
        assert act <= 4 and act >= 1
        zero_place = self.get_num(0)  # y,x of 0's place
        assert zero_place[0] != -1 and zero_place [1] != -1
            
        # Note: directional movements are based on the blank space, aka the 0
        # we basically just swap tiles depending on the move if it can be swapped
        if act == 1:  # up
            if not zero_place[0] == 0:  # cant move down if there is no tile above it
                move_tile = self.board[zero_place[0]-1][zero_place[1]]
                self.board[zero_place[0]-1][zero_place[1]] = 0
                self.board[zero_place[0]][zero_place[1]] = move_tile
        elif act == 2:  # down
            if not zero_place[0] == self.dimensions[1]-1:  # cant move up if there is no tile under it
                move_tile = self.board[zero_place[0]+1][zero_place[1]]
                self.board[zero_place[0]+1][zero_place[1]] = 0
                self.board[zero_place[0]][zero_place[1]] = move_tile
        elif act == 3:  # left
            if not zero_place[1] == 0:  # cant move right if there is no tile to the left of it
                move_tile = self.board[zero_place[0]][zero_place[1]-1]
                self.board[zero_place[0]][zero_place[1]-1] = 0
                self.board[zero_place[0]][zero_place[1]] = move_tile
        elif act == 4:  # right
            if not zero_place[1] == self.dimensions[0]-1:  # cant move left if theres no tile to the right of it
                move_tile = self.board[zero_place[0]][zero_place[1]+1]
                self.board[zero_place[0]][zero_place[1]+1] = 0
                self.board[zero_place[0]][zero_place[1]] = move_tile
        else:
            print("problem with action script")
    
    def get_num(self, num):
        ''' helper that finds the (index) position of a number within this board '''
        for y in range(self.dimensions[1]):
            for x in range(self.dimensions[0]):
                if self.board[y][x] == num:
                    return (y,x)
        return (-1,-1)
    
    def copy(self):
        ''' deep-copy function to help with creation of new action states '''
        p1 = Puzzle(self.dimensions[0], self.dimensions[1])
        p1.board = copy.deepcopy(self.board)
        return p1



class Node:
    ''' helper class to represent nodes in A*'''
    def __init__(self, state, move, action, parent): # init node (state) with puzzle 
        self.state = state  # state off the board, aka puzzle
        self.move = move  # aka g(n) = path_cost
        self.action = action  # int representing the previous move it took to get here
        self.parent = parent  # parent Node
        
    def show(self, weight=1.0):  # show node info
        out = "g(n) + h(n) = f(n) :: "
        out += str(self.move) + " + " + str(self.state.h()) + " = " + str(self.f(weight)) + "\n"
        out += "action: " + action_translation2[self.action] + "\n"
        out += self.state.show() + "\n"
        return out
    
    def __bool__(self):
        return bool(self.state)
    
    def __eq__(self, rhs):  # compare board states
        if isinstance(rhs, Node):
            return self.state == rhs.state  # and self.move == rhs.move
        return False
    
    def f(self, h_weight=1.0):  # weight = 1.2?, weight = 1.4
        return self.move + h_weight*self.state.h()
        
def a_star(puzzle_start, h_weight=1.0):
    '''
    Main Algorithm: A*
    -takes in starting puzzle, weight and global goal state
    uses manhattan distance heuristic h(n) 
    and path cost, aka sum(moves), g(n) 
    to search for puzzle solution node (with backtracked path)
    '''
    curr_node = Node(puzzle_start, 0, 0, None)
    frontier = [curr_node]  # priority queue
    reach = {}  # no repeats
    num_nodes = 1
    while len(frontier) != 0:
        curr_node = frontier.pop()  # get next node from frontier
        # print(curr_node.show(h_weight))  # show sequence in terminal (not necessary for final)
        if curr_node.state.h() == 0:  # checking for goal node
            # heuristic is 0 @ goal
            print("\n  *solution found*")  # yay
            return curr_node, num_nodes
        
        for new_node in expand(curr_node):  # expand current node if not the goal
            temp_key = str(new_node.state.board)  # stringified state is the key -> easier for hashing
            if temp_key not in reach or new_node.move < reach[temp_key].move:
                print(("  searching for solutions with " + str(num_nodes) + " nodes generated..."), end = "\r")
                num_nodes += 1  # repeated states arent added to the tree and arent counted

                j = len(frontier)-1
                while j >= 0 and frontier[j].f(h_weight) < new_node.f(h_weight):  # insertion sort for frontier priority
                    j -= 1
                frontier.insert(j+1, new_node)  # insert before the node we're looking at
                reach[temp_key] = new_node  # add node and key into reach (or replace if already existing)
    print("\n  NO solution found")
    return curr_node, num_nodes  # if goal node isnt found then we just return the last node we looked at
    # Note: this will also return the last seen/closest node to solution in case of failure as opposed to goal state

def expand(curr_node):
    ''' yields children of the current state as edited by various, allowed actions'''
    for i in range(1, 5):  # types of actions
        new_state = curr_node.state.copy()
        new_state.action(i)  # make a puzzle copy with the new action done
        new_node = Node(new_state, curr_node.move+1, i, curr_node)  # make new node out of new state
        if curr_node.state.board != new_node.state.board:  # no need to look at new actions that make no progress
            yield new_node  # generator for expanded next states


def trace_back(solution_node, h_weight):
    ''' returns information of the path solution based on the goal node '''
    depth = 0  # depth of tree
    action_sequence = []  # actions taken from start to goal
    f_sequence = []  # sequence of f(n) values
    
    curr_node = solution_node
    while curr_node != None:
        if curr_node.action != 0:  # append action if it is not the first node
            depth += 1  # inc depth
            action_sequence.insert(0, action_translation[curr_node.action])  # insert/queue into first position (order)
        f_sequence.insert(0, str( round(curr_node.f(h_weight), 2) ))  # rounded for easy of reading
        curr_node = curr_node.parent  # trace up to parent
    return depth, action_sequence, f_sequence


if __name__ == '__main__':
    print("start...")
    
    # input_files = ['Input1.txt', 'Input2.txt', 'Input3.txt']  #'Sample_Input.txt', 'test.txt'
    input_files = os.listdir(os.getcwd() + "/Input")  # get all files in input dir
    for file_i in range(len(input_files)):  # run code on all files in director
        start_board = Puzzle()  # set up puzzles
        weights = [1.0, 1.2, 1.4]  # set of weights to run algo for
        # no input neede since all 3 weights should be generated for the final solution (talked to Prof)
        line_num = 1  # keep track of line number to know which puzzle is which
        init_nums = []  # lists of values to enter into Puzzle class
        goal_nums = []
        for line in fileinput.FileInput(files = "Input/"+input_files[file_i]):  # .input
            nums = line.replace('\n', '').split(" ")  # take out breaks and seperate numbs
            # Note: spacing can be a bit finicky so be careful of not combined numbers
            for temp in nums: # edge case with appended empty char in array
                if temp == '':
                    nums.remove(temp)
            if line_num < 4:  # save init state
                for num in nums:
                    init_nums.append(int(num))
            elif line_num > 4 and line_num < 8:  # save goal state
                for num in nums:
                    goal_nums.append(int(num))
            line_num += 1
        start_board.fill(init_nums)   # fill start puzzle
        GOAL_BOARD = goal_nums  # overwrite default goal state (saved as global up top)
        temp_goal = Puzzle()
        temp_goal.fill(GOAL_BOARD)  # create temp goal board for initial validation
        assert bool(start_board)   # double check to see if its a valid puzzle and this code can handle it
        assert bool(temp_goal)

        file_num = 1
        print()  # spacing in terminal
        for weight in weights:  # get new output per weight
            print("Running Solution", file_num, "for", input_files[file_i])
            name = ""
            if file_num == 1:  # file naming convention per requirements pdf
                name = "a"
            elif file_num == 2:
                name = "b"
            else:
                name = "c"
                
            solution_node, num_nodes = a_star(start_board, weight)  # run algo
            depth, actions, f_sequence = trace_back(solution_node, weight)  # get extra information from traceback
            # assert bool(solution_node)  # double-check solution is okay
            
            # write the solution board in addition to all the other collected info
            f = open("Output/output"+str(file_i+1)+name+".txt", "w")  # create file if it doesnt exist
            f.write(start_board.show())
            f.write("\n")
            f.write(solution_node.state.show())
            f.write("\n")
            
            f.write(str(weight) + "\n")
            f.write(str(depth) + "\n")
            f.write(str(num_nodes) + "\n")
            f.write(" ".join(actions) + "\n")
            f.write(" ".join(f_sequence) + "\n")
            
            file_num += 1
            f.close()
    print("\nend...")