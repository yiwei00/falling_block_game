# falling blocks game (cannot use actual name for legal reasons)
from enum import Enum
import random
from copy import copy
from piece import *

LOCK_DELAY = 30

random.seed(None)

class action_t(Enum):
    NONE = 0
    LEFT = 1
    RIGHT = 2
    ROTATE_LEFT = 3
    ROTATE_RIGHT = 4
    HARD_DROP = 5
    SOFT_DROP = 6
    HOLD = 7
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

piece_set = [Piece(piece_t.J), Piece(piece_t.L), Piece(piece_t.O), Piece(piece_t.I), Piece(piece_t.T), Piece(piece_t.S), Piece(piece_t.Z)]
action_set = [action_t.NONE, action_t.LEFT, action_t.RIGHT, action_t.HARD_DROP, action_t.ROTATE_LEFT, action_t.ROTATE_RIGHT, action_t.HOLD]

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
            c = '[A]'
        return c

class BlockGame:
    def __init__(self, start_lvl = 1, line_limit = 300):
        self.start_lvl = min(start_lvl, 16)
        self.line_limit = line_limit
        self.reset()

    def reset(self):
        self.width = 10
        self.height = 20
        self.buffer = 20
        self.true_height = self.height + self.buffer

        self.board = [[Cell(x, y) for x in range(self.width)] for y in range(self.height + self.buffer)]
        self.block_queue = []

        # Drop the first piece
        self.bag = n_bag(piece_set)
        self.spawn_pos = (self.buffer - 2, self.width//2 -1)
        self.active_piece = None
        self.active_piece_pos = (0, 0)
        self.drop_piece(self.bag.grab_item())

        # actions
        self.last_action = action_t.NONE
        self.soft_dropping = False
        self.soft_drop_fpl = 8

        # misc state keeping
        self.is_over = False
        self.hard_drop = False

        # hold piece
        self.just_held = False
        self.hold_piece = None

        # game speed
        self.game_speed_curve = [
            60, 56, 51, 47, 43, 38, 34, 30, 25, 21, 17, 12, 8, 4, 1, 0
        ]
        self.frames_per_line = self.game_speed_curve[self.start_lvl - 1]
        self.frame_count = 0
        self.last_fall_frame = 0

        # lock delay
        self.RESET_LIMIT = 15
        self.lock_delay_started = False
        self.lock_time = 0
        self.n_resets = 0

        # score keeping
        self.score = 0
        self.line_count = 0
        self.combo_count = -1
        self.level = self.start_lvl

        # t-trick
        self.t_trick_possible = False
        self.t_trick_offset = (0, 0)


    def set_action(self, action):
        self.last_action = action

    def can_fit(self, piece, pos):
        center = piece.center
        for row in range(len(piece.shape)):
            for col in range(len(piece.shape[row])):
                if piece.shape[row][col] == 1:
                    r = pos[0] + (row - center[0])
                    c = pos[1] + (col - center[1])
                    if (r < 0 or r >= self.true_height or c < 0 or c >= self.width):
                        return False
                    if self.board[r][c].state == 1:
                        return False
        return True

    def move_active_piece(self, offset):
        if offset == (0, 0):
            return False
        new_loc = (self.active_piece_pos[0] + offset[0], self.active_piece_pos[1] + offset[1])
        possible = self.can_fit(self.active_piece, new_loc)
        if possible:
            self.active_piece_pos = new_loc
        return possible

    def soft_reset_lock_delay(self):
        if self.n_resets < self.RESET_LIMIT:
            self.lock_time = self.frame_count
            self.n_resets += 1

    def hard_reset_lock_delay(self):
        self.lock_time = self.frame_count
        self.n_resets = 0
        self.lock_delay_started = False

    def start_lock_delay(self):
        if self.lock_delay_started:
            return
        self.lock_time = self.frame_count
        self.n_resets = 0
        self.lock_delay_started = True

    # return true lock delay allows it
    def should_lock(self):
        if self.lock_delay_started:
            over_time = (self.frame_count - self.lock_time) >= LOCK_DELAY
            if over_time:
                self.hard_reset_lock_delay()
            return over_time
        return False

    def can_active_fall(self):
        return self.can_fit(self.active_piece, (self.active_piece_pos[0] + 1, self.active_piece_pos[1]))

    def try_rotate_piece(self, dir):
        dir = dir % 4
        if dir == 0:
            return False
        rotated_piece = self.active_piece.rotate_n_copy(dir)
        new_rot = rotated_piece.rotation
        old_rot = self.active_piece.rotation
        p_type = self.active_piece.piece_type
        match p_type:
            case piece_t.O:
                kick_offset_table = kick_offset_o
            case piece_t.I:
                kick_offset_table = kick_offset_i
            case default:
                kick_offset_table = kick_offset_default
        kick_offsets = []
        for i in range(len(kick_offset_table[0])):
            kick_offsets.append((
                kick_offset_table[old_rot][i][0] - kick_offset_table[new_rot][i][0],
                kick_offset_table[old_rot][i][1] - kick_offset_table[new_rot][i][1]
            ))
        for offset in kick_offsets:
            if self.can_fit(
                rotated_piece,
                (self.active_piece_pos[0] + offset[0], self.active_piece_pos[1] + offset[1])
            ):
                if p_type == piece_t.T:
                    self.t_trick_possible = True
                    self.t_trick_offset = offset
                else:
                    self.t_trick_possible = False
                self.active_piece = rotated_piece
                self.active_piece_pos = (self.active_piece_pos[0] + offset[0], self.active_piece_pos[1] + offset[1])
                return True
        return False


    def next_state(self):
        if self.is_over:
            return
        if self.active_piece is None:
            self.drop_piece(self.bag.grab_item())
        center = self.active_piece.center
        # process action
        offset = (0, 0)
        rot_dir = 0
        match self.last_action:
            case action_t.NONE:
                pass
            case action_t.LEFT:
                offset = (0, -1)
                pass
            case action_t.RIGHT:
                offset = (0, 1)
                pass
            case action_t.HARD_DROP:
                self.hard_drop = True
                pass
            case action_t.SOFT_DROP:
                self.soft_dropping = not self.soft_dropping
                pass
            case action_t.ROTATE_LEFT:
                rot_dir = -1
                pass
            case action_t.ROTATE_RIGHT:
                rot_dir = 1
                pass
            case action_t.HOLD:
                if not self.just_held:
                    self.just_held = True
                    self.hard_reset_lock_delay()
                    if self.hold_piece is None:
                        self.hold_piece = self.active_piece.piece_type
                        self.drop_piece(self.bag.grab_item())
                    else:
                        temp_piece = self.active_piece.piece_type
                        self.drop_piece(Piece(self.hold_piece))
                        self.hold_piece = temp_piece
                pass
            case default:
                print('Unimplemented action: ' + str(self.last_action.name))
        self.last_action = action_t.NONE
        # count frames
        self.frame_count += 1
        # rotate piece
        move_success = False
        if rot_dir != 0:
            if (self.try_rotate_piece(rot_dir)):
                move_success = True
        # move piece
        if (self.move_active_piece(offset)):
            move_success = True
            self.t_trick_possible = False
        if self.hard_drop:
            while self.move_active_piece((1, 0)):
                pass
        # soft reset lock delay if move was successful
        if move_success:
            self.soft_reset_lock_delay()
        # see if time to fall, and if so, fall
        # if at bottom, start lock delay if not started
        # if fall, then reset lock delay
        can_fall = self.can_active_fall()
        if can_fall:
            if self.frames_per_line == 0:
                while self.move_active_piece((1, 0)):
                    self.hard_reset_lock_delay()
                    self.last_fall_frame = self.frame_count
            elif (
                    ((self.frame_count - self.frames_per_line) % self.frames_per_line == 0) or
                    (self.soft_dropping and (self.frame_count - self.last_fall_frame) >= self.soft_drop_fpl)
                ):
                if self.move_active_piece((1, 0)):
                    self.hard_reset_lock_delay()
                    self.last_fall_frame = self.frame_count
        elif not self.lock_delay_started:
                self.start_lock_delay()
        if (not can_fall) and (self.hard_drop or (self.should_lock())):
            # setting active into board
            t_trick = 0
            self.hard_drop = False
            self.hard_reset_lock_delay()
            lock_on_visible = False
            for row in range(len(self.active_piece.shape)):
                for col in range(len(self.active_piece.shape[row])):
                    if self.active_piece.shape[row][col] == 1:
                        r = self.active_piece_pos[0] + (row - center[0])
                        c = self.active_piece_pos[1] + (col - center[1])
                        self.board[r][c].state = 1
                        if r > self.buffer:
                            lock_on_visible = True
            if not lock_on_visible: # if set above the visible board, game over
                self.is_over = True
            else:
                # reset held
                self.just_held = False
                # check for t-trick
                if self.active_piece.piece_type == piece_t.T and self.t_trick_possible:
                    match self.active_piece.rotation:
                        case 0:
                            front_pos = [
                                (0, 0), (0, 2)
                            ]
                            back_pos = [
                                (2, 0), (2, 2)
                            ]
                        case 1:
                            front_pos = [
                                (0, 2), (2, 2)
                            ]
                            back_pos = [
                                (0, 0), (2, 0)
                            ]
                        case 2:
                            front_pos = [
                                (2, 0), (2, 2)
                            ]
                            back_pos = [
                                (0, 0), (0, 2)
                            ]
                        case 3:
                            front_pos = [
                                (2, 2), (0, 2)
                            ]
                            back_pos = [
                                (2, 0), (0, 0)
                            ]
                        case default:
                            raise Exception('Invalid rotation: ' + str(self.active_piece.rotation))
                    front_obs, back_obs = 0, 0
                    for pos in front_pos:
                        r = self.active_piece_pos[0] + (pos[0] - center[0])
                        c = self.active_piece_pos[1] + (pos[1] - center[1])
                        if self.board[r][c].state == 1:
                            front_obs += 1
                    for pos in back_pos:
                        r = self.active_piece_pos[0] + (pos[0] - center[0])
                        c = self.active_piece_pos[1] + (pos[1] - center[1])
                        if self.board[r][c].state == 1:
                            back_obs += 1
                    if front_obs == 2 and back_obs > 0:
                        t_trick = 2
                    elif back_obs == 2 and front_obs > 0:
                        if (
                            (abs(self.t_trick_offset[1]) + abs(self.t_trick_offset[0])) >= 3
                        ):
                            t_trick = 2
                        t_trick = 1
                    self.t_trick_possible = False
                # check for clear
                clear_count = 0
                while True:
                    found_clear = False
                    for r in range(self.true_height - 1, -1, -1):
                        if all([self.board[r][c].state == 1 for c in range(self.width)]):
                            found_clear = True
                            clear_count += 1
                            for c in range(self.width):
                                self.board[r][c].state = 0
                            for r_2 in range(r, 0, -1):
                                for c_2 in range(self.width):
                                    self.board[r_2][c_2].state = self.board[r_2-1][c_2].state
                    if not found_clear:
                        break
                self.line_count += clear_count
                # scoring
                t_trick_score = 0
                line_score = 0
                combo_score = 0
                if t_trick == 1:
                    t_trick_score = 100
                elif t_trick == 2:
                    t_trick_score = 400
                if clear_count > 0:
                    self.combo_count += 1
                    line_score = 0
                    match clear_count:
                        case 1:
                            line_score = 100
                            if t_trick == 1:
                                t_trick_score = 200
                            elif t_trick == 2:
                                t_trick_score = 800
                            else:
                                t_trick_score = 0
                        case 2:
                            line_score = 300
                            if t_trick == 1:
                                t_trick_score = 400
                            elif t_trick == 2:
                                t_trick_score = 1200
                            else:
                                t_trick_score = 0
                        case 3:
                            line_score = 500
                            if t_trick > 0:
                                t_trick_score = 1600
                        case 4:
                            line_score = 800
                        case default:
                            raise Exception('Invalid clear count: ' + str(clear_count))
                    combo_score = 50 * (self.combo_count)
                else:
                    self.combo_count = -1

                self.score += (line_score + combo_score + t_trick_score) * self.level
                # end game if over line limit
                if self.line_count >= self.line_limit:
                    self.is_over = True
                    return
                # update level
                self.level = self.start_lvl + self.line_count // 10
                self.level = min(self.level, 16)
                # update gravity
                self.frames_per_line = self.game_speed_curve[self.level - 1]
                # turn off soft drop
                self.soft_dropping = False
                # drop new piece
                self.drop_piece(self.bag.grab_item())

    # update board state with active
    def update_board(self):
        # remove current active piece
        for row in range(self.true_height):
            for col in range(self.width):
                if self.board[row][col].state == 2:
                    self.board[row][col].state = 0
        # add active piece
        center = self.active_piece.center
        for row in range(len(self.active_piece.shape)):
            for col in range(len(self.active_piece.shape[row])):
                if self.active_piece.shape[row][col] == 1:
                    r = self.active_piece_pos[0] + (row - center[0])
                    c = self.active_piece_pos[1] + (col - center[1])
                    self.board[r][c].state = 2

    def get_visible_board(self):
        display_board = [[Cell(x, y) for x in range(self.width)] for y in range(self.height)]
        for row in range(self.buffer, self.true_height):
            for col in range(self.width):
                display_board[row - self.buffer][col].state = self.board[row][col].state
        center = self.active_piece.center
        active_piece_disp_pos = (self.active_piece_pos[0] - self.buffer, self.active_piece_pos[1])
        for row in range(len(self.active_piece.shape)):
            for col in range(len(self.active_piece.shape[row])):
                if (active_piece_disp_pos[0] < 0 or
                    active_piece_disp_pos[0] >= self.height or
                    active_piece_disp_pos[1] < 0 or
                    active_piece_disp_pos[1] >= self.width
                ):
                    continue
                if self.active_piece.shape[row][col] == 1:
                    r = active_piece_disp_pos[0] + (row - center[0])
                    c = active_piece_disp_pos[1] + (col - center[1])
                    if r < 0 or r >= self.height or c < 0 or c >= self.width:
                        continue
                    display_board[r][c].state = 2
        return display_board

    def get_preview_pieces(self, n):
        if n > 7:
            n = 7
        indices = self.bag.preview_bag(n)
        pieces = []
        for i in indices:
            pieces.append(copy(piece_set[i]))
        return pieces


    def __str__(self):
        board_to_print = self.get_visible_board()
        s = ''
        for row in range(self.height):
            line = ''
            for col in range(self.width):
                line += str(board_to_print[row][col])
            s += line + '\n'
        return s

    def drop_piece(self, piece):
        self.active_piece = piece
        self.active_piece_pos = self.spawn_pos

        # if spawning on top of another piece, set game over
        if not self.can_fit(self.active_piece, self.active_piece_pos):
            self.is_over = True