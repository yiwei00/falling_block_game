# falling blocks game
from enum import Enum
import random
from copy import copy
from block_game_pieces import *

# TODO: change input to be 2-tuple ()
class input_t(Enum):
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
        self.bag = []
        self.gen_next_bag()

    def preview_bag(self, n):
        if n > self.n:
            n = self.n
        indices = self.bag[-n:]
        return [self.item_set[i] for i in indices]

    def gen_next_bag(self):
        new_ord = list(range(self.n))
        random.shuffle(new_ord)
        self.bag = new_ord + self.bag

    def grab_item(self):
        item_idx = self.bag.pop()
        if len(self.bag) < self.n:
            self.gen_next_bag()
        return copy(self.item_set[item_idx])

piece_set = copy(list(piece_t))
input_set = copy(list(input_t))

std_piece_set = [
    piece_t.J, piece_t.L, piece_t.O, piece_t.I, piece_t.T, piece_t.S, piece_t.Z
]
dot_piece_set = [piece_t.dot]
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
    def __init__(self,
        seed = None,
        start_lvl = 1,
        line_limit = 150,
        set_speed = None,
        starting_board = None,
        piece_subset = std_piece_set,
        **kwargs
    ):
        if seed is not None:
            random.seed(seed)
        # level parameters
        self.start_lvl = min(start_lvl, 15)
        self.line_limit = line_limit
        self.set_speed = set_speed
        if self.set_speed is not None:
            self.game_speed_curve = lambda x: self.set_speed
        else:
            self.game_speed_curve = lambda i: [
                60, 56, 51, 47, 43, 38, 34, 30, 25, 21, 17, 12, 8, 4, 0
            ][i]
        self.starting_board = starting_board
        self.piece_subset = piece_subset
        # board variables
        self.width = 10
        self.height = 20
        self.buffer = 20
        self.true_height = self.height + self.buffer
        self.spawn_pos = (self.buffer - 2, self.width//2 -1)
        # game variables
        self.RESET_LIMIT = 15
        self.lock_delay_dur = 30

        self.reset()

    def reset(self):
        # regenerate board
        self.board = [[Cell(x, y) for x in range(self.width)] for y in range(self.height + self.buffer)]
        if self.starting_board is not None:
            for row in range(len(self.starting_board)):
                for col in range(len(self.starting_board[row])):
                    self.board[self.buffer + row][col].state = self.starting_board[row][col]

        # Drop the first piece
        if self.piece_subset is None:
            self.bag = n_bag(piece_set)
        else:
            if all([p in piece_set for p in self.piece_subset]):
                self.bag = n_bag(self.piece_subset)
            else:
                raise Exception('Invalid piece subset')
        self.active_piece = None
        self.active_piece_pos = (0, 0)
        self.drop_piece(self.bag.grab_item())

        # input
        self.input_queue = []

        # misc state keeping
        self.is_over = False
        self.reach_line_limit = False
        self.hard_drop = False
        self.is_full_clear = False

        # hold piece
        self.just_held = False
        self.hold_piece = None

        # game speed
        self.frames_per_line = self.game_speed_curve(self.start_lvl - 1)
        self.frame_count = 0
        self.last_fall_frame = 0

        # lock delay
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


    def set_input(self, input):
        self.input_queue.append(input)

    def handle_controlled_movement(self, offset, rot_dir):
        move_success = False
        if rot_dir != 0:
            if (self.try_rotate_piece(rot_dir)):
                move_success = True
        # move piece
        if (self.move_active_piece(offset)):
            move_success = True
            self.t_trick_possible = False
        # hard drop
        if self.hard_drop:
            while self.move_active_piece((1, 0)):
                pass
        # reset lock delay
        if move_success:
            self.soft_reset_lock_delay()

    def swap_hold(self):
        if self.just_held:
            return
        self.just_held = True
        self.hard_reset_lock_delay()
        if self.hold_piece is None:
            self.hold_piece = self.active_piece.piece_type
            self.drop_piece(self.bag.grab_item())
        else:
            temp_piece = self.active_piece.piece_type
            self.drop_piece(self.hold_piece)
            self.hold_piece = temp_piece

    def handle_inputs(self):
        if self.input_queue == []:
            return
        # TODO: reconsider whether to bundle all movement into one offset
        # TODO: when soft dropping, prevent normal falling?
        # TODO: when reworking "speed", change soft drop to be a multiplier
        offset = (0, 0)
        rot_dir = 0
        for input in self.input_queue:
            match input:
                case input_t.LEFT:
                    offset = (offset[0], offset[1] - 1)
                case input_t.RIGHT:
                    offset = (offset[0], offset[1] + 1)
                case input_t.SOFT_DROP:
                    offset = (offset[0] + 1, offset[1])
                case input_t.HARD_DROP:
                    self.hard_drop = True
                case input_t.ROTATE_LEFT:
                    rot_dir = -1
                case input_t.ROTATE_RIGHT:
                    rot_dir = 1
                case input_t.HOLD:
                    self.swap_hold()
                case default:
                    print('Unimplemented input: ' + str(self.input.name))
        self.input_queue = []
        self.handle_controlled_movement(offset, rot_dir)


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

    def should_lock(self):
        if self.lock_delay_started:
            over_time = (self.frame_count - self.lock_time) >= self.lock_delay_dur
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
            case piece_t.dot:
                kick_offset_table = kick_offset_dot
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

    def update_state(self):
        # check if game is over
        if self.is_over or self.reach_line_limit:
            return
        # drop new piece if none
        if self.active_piece is None:
            self.drop_piece(self.bag.grab_item())
        # count frames
        self.frame_count += 1
        # update state based on player input
        self.handle_inputs()

        # TODO: move to function (name in progress) "pre_fall_stage"
        #region handle falling
        can_fall = self.can_active_fall()
        if can_fall:
            # if "gravity" is max, fall immediately
            if self.frames_per_line == 0:
                while self.move_active_piece((1, 0)):
                    self.hard_reset_lock_delay()
                    self.last_fall_frame = self.frame_count
            # otherwise wait for fall delay then fall
            elif (((self.frame_count) % self.frames_per_line == 0)):
                if self.move_active_piece((1, 0)):
                    self.hard_reset_lock_delay()
                    self.last_fall_frame = self.frame_count
        # if at bottom, start lock delay if not already started
        elif not self.lock_delay_started:
                self.start_lock_delay()
        #endregion

        if (not can_fall) and (self.hard_drop or (self.should_lock())):
            # this big block is for handling both locking and what happens after a piece locks
            # The real start of the spaghetti
            # TODO: divide into sections:
            #    1. locking,
            #    2. row-clear logic,
            #    3. trick detection logic,
            #    4. scoring,
            #    5. internal update
            # setting active into board
            t_trick = 0
            self.hard_drop = False
            self.hard_reset_lock_delay()
            lock_on_visible = False
            for row in range(len(self.active_piece.shape)):
                for col in range(len(self.active_piece.shape[row])):
                    if self.active_piece.shape[row][col] == 1:
                        r = self.active_piece_pos[0] + (row - self.active_piece.center[0])
                        c = self.active_piece_pos[1] + (col - self.active_piece.center[1])
                        if (r < 0 or r >= self.true_height or c < 0 or c >= self.width):
                            continue
                        self.board[r][c].state = 1
                        if r > self.buffer:
                            lock_on_visible = True
            if not lock_on_visible: # if set above the visible board, game over
                self.is_over = True
            # this else marks the start of the "scoring" section
            else:
                self.is_full_clear = False
                # reset held
                self.just_held = False
                # check for t-trick TODO: move to function, (safe to put after row-clear logic?)
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
                        r = self.active_piece_pos[0] + (pos[0] - self.active_piece.center[0])
                        c = self.active_piece_pos[1] + (pos[1] - self.active_piece.center[1])
                        if (r < 0 or r >= self.true_height or c < 0 or c >= self.width):
                            continue
                        if self.board[r][c].state == 1:
                            front_obs += 1
                    for pos in back_pos:
                        r = self.active_piece_pos[0] + (pos[0] - self.active_piece.center[0])
                        c = self.active_piece_pos[1] + (pos[1] - self.active_piece.center[1])
                        if (r < 0 or r >= self.true_height or c < 0 or c >= self.width):
                            continue
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
                # check for clear TODO: move to function
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
                if clear_count > 0:
                    self.is_full_clear = all(
                        all(
                            [self.board[r][c].state != 1 for c in range(self.width)]
                        ) for r in range(self.true_height)
                    )
                # scoring #TODO: move to function
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
                    self.reach_line_limit = True
                    return
                # update level
                self.level = self.start_lvl + self.line_count // 10
                self.level = min(self.level, 15)
                # update gravity
                self.frames_per_line = self.game_speed_curve(self.level - 1)
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
        return self.bag.preview_bag(n)


    def __str__(self):
        board_to_print = self.get_visible_board()
        s = ''
        for row in range(self.height):
            line = ''
            for col in range(self.width):
                line += str(board_to_print[row][col])
            s += line + '\n'
        hold = '?' if self.hold_piece is None else self.hold_piece.name
        next_pieces = ' '.join(f'[{p.name}]' for p in self.get_preview_pieces(5))
        s += f'Hold: {hold} | Next: {next_pieces}\n'
        s += f'Score: {self.score} | Lines: {self.line_count}/{self.line_limit} | Level: {self.level}\n'
        return s

    def drop_piece(self, piece):
        self.active_piece = Piece(piece)
        self.active_piece_pos = self.spawn_pos

        # if spawning on top of another piece, set game over
        if not self.can_fit(self.active_piece, self.active_piece_pos):
            self.is_over = True