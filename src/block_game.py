# falling blocks game (cannot use actual name for legal reasons)
from enum import Enum
import random
from copy import copy
''' TODO: Remove this comment block
actions:
left, right, hard drop, rotate left, rotate right, hold, none
'''

random.seed(None)

class Action(Enum):
    NONE = 0
    LEFT = 1
    RIGHT = 2
    HARD_DROP = 3
    ROTATE_LEFT = 4
    ROTATE_RIGHT = 5
    HOLD = 6
    def __repr__(self) -> str:
        return super().__repr__()

class piece_t(Enum):
    J = 1
    L = 2
    O = 3
    I = 4
    T = 5
    S = 6
    Z = 7
    def __repr__(self) -> str:
        return super().__repr__()

class n_bag:
    def __init__(self, item_set):
        self.item_set = item_set
        self.n = len(self.item_set)
        self.bag_index = 0
        self.bag = []
        self.gen_next_bag()

    def preview_bag(self, n):
        if n > self.n:
            n = self.n
        return self.bag[:n]

    def gen_next_bag(self):
        new_ord = list(range(self.n))
        random.shuffle(new_ord)
        self.bag = new_ord + self.bag

    def grab_item(self):
        item_idx = self.bag.pop()
        if len(self.bag) < self.n:
            self.gen_next_bag()
        return copy(self.item_set[item_idx])

class Piece:
    def __init__(self, piece_type):
        self.piece_type = piece_type
        self.rotation = 0
        self.center = (1,1)
        match piece_type:
            case piece_t.J:
                self.shape = [[1, 0, 0],
                              [1, 1, 1],
                              [0, 0, 0]]
            case piece_t.L:
                self.shape = [[0, 0, 1],
                              [1, 1, 1],
                              [0, 0, 0]]
            case piece_t.O:
                self.shape = [[0, 1, 1],
                              [0, 1, 1],
                              [0, 0, 0]]
            case piece_t.I:
                self.shape = [[0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 1, 1, 1, 1],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0]]
                self.center = (2,2)
            case piece_t.T:
                self.shape = [[0, 1, 0],
                              [1, 1, 1],
                              [0, 0, 0]]
            case piece_t.S:
                self.shape = [[0, 1, 1],
                              [1, 1, 0],
                              [0, 0, 0]]
            case piece_t.Z:
                self.shape = [[1, 1, 0],
                              [0, 1, 1],
                              [0, 0, 0]]

piece_set = [Piece(piece_t.J), Piece(piece_t.L), Piece(piece_t.O), Piece(piece_t.I), Piece(piece_t.T), Piece(piece_t.S), Piece(piece_t.Z)]

class Cell:
    def __init__(self, x, y, state=0):
        self.x = x
        self.y = y
        self.state = state # 0 = empty, 1 = set

    def __str__(self) -> str:
        c = '[ ]'
        if self.state == 1:
            c = '[#]'
        if self.state == 2:
            c = '[*]'
        return c

class BlockGame:
    def __init__(self):
        self.width = 10
        self.height = 20
        self.buffer = 20
        self.true_height = self.height + self.buffer

        self.board = [[Cell(x, y) for x in range(self.width)] for y in range(self.height + self.buffer)]
        self.block_queue = []

        # Drop the first piece
        self.bag = n_bag(piece_set)
        self.spawn_pos = (self.buffer - 1, self.width//2 -1)
        self.active_piece = None
        self.active_piece_pos = (0, 0)
        self.drop_piece(self.bag.grab_item())

    def set_action(self, action):
        pass

    def next_state(self):
        if self.active_piece is None:
            pass
        else:
            # see if piece can fall
            center = self.active_piece.center
            attempt_pos = (self.active_piece_pos[0] + 1, self.active_piece_pos[1])
            fall_possible = True
            for row in range(len(self.active_piece.shape)):
                for col in range(len(self.active_piece.shape[row])):
                    if self.active_piece.shape[row][col] == 1:
                        r = attempt_pos[0] + (row - center[0])
                        c = attempt_pos[1] + (col - center[1])
                        if self.board[r][c].state == 1:
                            fall_possible = False
                            break
                if fall_possible:
                    break
            if fall_possible: # fall down!
                self.active_piece_pos = attempt_pos
            else: # set piece
                for row in range(len(self.active_piece.shape)):
                    for col in range(len(self.active_piece.shape[row])):
                        if self.active_piece.shape[row][col] == 1:
                            r = self.active_piece_pos[0] + (row - center[0])
                            c = self.active_piece_pos[1] + (col - center[1])
                            self.board[r][c].state = 1
                self.drop_piece(self.bag.grab_item())
        pass

    def __str__(self):
        s = ''
        for row in range(self.buffer, self.true_height):
            line = ''
            for col in range(self.width):
                if (row, col) == self.active_piece_pos:
                    line += '[A]'
                else:
                    line += str(self.board[row][col])
            s += line + '\n'
        return s

    def drop_piece(self, piece):
        self.active_piece = piece
        self.active_piece_pos = self.spawn_pos
        center = self.active_piece.center
        for row in range(len(piece.shape)):
            for col in range(len(piece.shape[row])):
                if piece.shape[row][col] == 1:
                    r = self.active_piece_pos[0] + (row - center[0])
                    c = self.active_piece_pos[1] + (col - center[1])
                    self.board[r][c].state = 2
# Create a new game
game = BlockGame()

# Print the game board
print(game)