from enum import Enum

class piece_t(Enum):
    J = 0
    L = 1
    O = 2
    I = 3
    T = 4
    S = 5
    Z = 6
    def __repr__(self) -> str:
        return super().__repr__()

class Piece:
    def __init__(self, piece_type, rotation=0):
        self.piece_type = piece_type
        self.rotation = rotation
        self.center = (1,1) if piece_type != piece_t.I else (2,2)
        # big match statement to handle all the rotations
        # uncollapse at your own risk
        match (self.piece_type, self.rotation):
            case (piece_t.J, 0):
                self.shape = [[1, 0, 0],
                              [1, 1, 1],
                              [0, 0, 0]]
            case (piece_t.J, 1):
                self.shape = [[0, 1, 1],
                              [0, 1, 0],
                              [0, 1, 0]]
            case (piece_t.J, 2):
                self.shape = [[0, 0, 0],
                              [1, 1, 1],
                              [0, 0, 1]]
            case (piece_t.J, 3):
                self.shape = [[0, 1, 0],
                              [0, 1, 0],
                              [1, 1, 0]]
            case (piece_t.L, 0):
                self.shape = [[0, 0, 1],
                              [1, 1, 1],
                              [0, 0, 0]]
            case (piece_t.L, 1):
                self.shape = [[0, 1, 0],
                              [0, 1, 0],
                              [0, 1, 1]]
            case (piece_t.L, 2):
                self.shape = [[0, 0, 0],
                              [1, 1, 1],
                              [1, 0, 0]]
            case (piece_t.L, 3):
                self.shape = [[1, 1, 0],
                              [0, 1, 0],
                              [0, 1, 0]]
            case (piece_t.O, 0):
                self.shape = [[0, 1, 1],
                              [0, 1, 1],
                              [0, 0, 0]]
            case (piece_t.O, 1):
                self.shape = [[0, 0, 0],
                              [0, 1, 1],
                              [0, 1, 1]]
            case (piece_t.O, 2):
                self.shape = [[0, 0, 0],
                              [1, 1, 0],
                              [1, 1, 0]]
            case (piece_t.O, 3):
                self.shape = [[1, 1, 0],
                              [1, 1, 0],
                              [0, 0, 0]]
            case (piece_t.I, 0):
                self.shape = [[0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 1, 1, 1, 1],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0]]
            case (piece_t.I, 1):
                self.shape = [[0, 0, 0, 0, 0],
                              [0, 0, 1, 0, 0],
                              [0, 0, 1, 0, 0],
                              [0, 0, 1, 0, 0],
                              [0, 0, 1, 0, 0]]
            case (piece_t.I, 2):
                self.shape = [[0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [1, 1, 1, 1, 0],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0]]
            case (piece_t.I, 3):
                self.shape = [[0, 0, 1, 0, 0],
                              [0, 0, 1, 0, 0],
                              [0, 0, 1, 0, 0],
                              [0, 0, 1, 0, 0],
                              [0, 0, 0, 0, 0]]
            case (piece_t.T, 0):
                self.shape = [[0, 1, 0],
                              [1, 1, 1],
                              [0, 0, 0]]
            case (piece_t.T, 1):
                self.shape = [[0, 1, 0],
                              [0, 1, 1],
                              [0, 1, 0]]
            case (piece_t.T, 2):
                self.shape = [[0, 0, 0],
                              [1, 1, 1],
                              [0, 1, 0]]
            case (piece_t.T, 3):
                self.shape = [[0, 1, 0],
                              [1, 1, 0],
                              [0, 1, 0]]
            case (piece_t.S, 0):
                self.shape = [[0, 1, 1],
                              [1, 1, 0],
                              [0, 0, 0]]
            case (piece_t.S, 1):
                self.shape = [[0, 1, 0],
                              [0, 1, 1],
                              [0, 0, 1]]
            case (piece_t.S, 2):
                self.shape = [[0, 0, 0],
                              [0, 1, 1],
                              [1, 1, 0]]
            case (piece_t.S, 3):
                self.shape = [[1, 0, 0],
                              [1, 1, 0],
                              [0, 1, 0]]
            case (piece_t.Z, 0):
                self.shape = [[1, 1, 0],
                              [0, 1, 1],
                              [0, 0, 0]]
            case (piece_t.Z, 1):
                self.shape = [[0, 0, 1],
                              [0, 1, 1],
                              [0, 1, 0]]
            case (piece_t.Z, 2):
                self.shape = [[0, 0, 0],
                              [1, 1, 0],
                              [0, 1, 1]]
            case (piece_t.Z, 3):
                self.shape = [[0, 1, 0],
                              [1, 1, 0],
                              [1, 0, 0]]
            case default:
                pass
        pass
    def rotate_n_copy(self, dir):
        dir = (dir + self.rotation) % 4
        return Piece(self.piece_type, dir)

kick_offset_default = {
    0: [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
    1: [(0, 0), (0, 1), (1, 1), (-2, 0), (-2, 1)],
    2: [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
    3: [(0, 0), (0, -1), (1,-1), (-2, 0), (-2,-1)]
}

kick_offset_i = {
    0: [(0, 0), (0, -1), (0, 2), (0,-1), (0, 2)],
    1: [(0, -1), (0, 0), (0, 0), (-1, 0), (2, 0)],
    2: [(-1, -1), (-1, 1), (-1, -2), (0, 1), (0, -2)],
    3: [(-1, 0), (-1, 0), (-1, 0), (1, 0), (-2, 0)]
}

kick_offset_o = {
    0: [(0, 0)],
    1: [(1, 0)],
    2: [(1, -1)],
    3: [(0, -1)]
}