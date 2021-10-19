# Kora S. Hughes - Artificial Intelligence Project 1: 11 Puzzel Problem with A*

""" PROJECT NOTES
1-2 students per project
“Bramble system” → only 1 tile moves at a time

standard:
 -11 tile problem
 -3 X 4 board
"""

import random
import copy


class Puzzle:
    '''
    Main Puzzle Class:
    - contains board and helper functions to navigate board
    '''
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
        nums = []
        for y in self.board:  # is valid if all unique nums within size
            for x in y:
                assert type(x) == int
                if x in nums or x < 0 or x > self.size:
                    return False
                else:
                    nums.append(x)
        return True

    def show(self):  # show the board for testing
        print("*BOARD* " + str(self.size) + "-Puzzle: " + str(self.dimensions))
        for y in self.board:
            out = ""
            for x in y:
                out += " " + str(x)
            print("[" + out + " ]")

    def random_fill(self):  # randomizer for board values in testing
        nums = random.sample(range(0, self.size+1), self.size+1)
        # print("adding random board:", nums)
        self.fill(nums)

    def fill(self, vals):
        '''
        :param vals: 1d array of puzzle values
        fills table
        '''
        assert len(vals) == self.size+1
        i = 0
        for y in range(0, self.dimensions[1]):
            for x in range(0, self.dimensions[0]):
                # print(vals[i], ":", x, ",", y, ",", i)
                self.board[y][x] = vals[i]
                i += 1



if __name__ == '__main__':
    print("start...\n")

    p1 = Puzzle()
    p1.show()
    print("Is valid puzzle?:", bool(p1))

    print()
    p1.random_fill()
    p1.show()
    print("Is valid puzzle?:", bool(p1))

    print("\nend...")


