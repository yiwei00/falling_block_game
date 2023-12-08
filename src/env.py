import numpy as np
from block_game import *
from gymnasium import Env as GymEnv, spaces
from stable_baselines3.common.env_checker import check_env

def piece2num(piece):
    return piece.piece_type.value

def num2act(num):
    return action_t(num)

class BlockGameEnv(GymEnv):
    def __init__(self, n_preview=5, line_limit=150):
        self.n_preview = n_preview
        self.game = BlockGame()
        self.prev_score = 0

        board_size = self.game.width * self.game.height
        board_space = [3] * board_size
        preview_space = [7] * n_preview
        misc_space = [8, 2, line_limit//10 + 2, 16, line_limit + 1, line_limit + 2]

        self.action_space = spaces.Discrete(len(action_t))
        self.observation_space = spaces.MultiDiscrete(board_space + preview_space + misc_space)


    def reset(self, seed = None):
        self.game = BlockGame(seed = seed)
        self.prev_score = 0
        state = self.get_state()
        return state, {}

    def step(self, action):
        self.game.set_action(num2act(action))
        self.game.update_state()
        new_score = self.game.score
        reward = new_score - self.prev_score
        self.prev_score = new_score
        return self.get_state(), reward, self.game.is_over, False, {}

    def get_state(self):
        state_board = np.zeros((
            self.game.height,
            self.game.width
        ), dtype=np.int32)
        visible_board = self.game.get_visible_board()
        for r in range(self.game.height):
            for c in range(self.game.width):
                state_board[r][c] = visible_board[r][c].state
        preview = self.game.get_preview_pieces(self.n_preview)
        preview_arr = np.zeros(self.n_preview, dtype=np.int32)
        for i in range(self.n_preview):
            preview_arr[i] = piece2num(preview[i])
        flat_board = state_board.flatten()
        preview_arr = preview_arr.flatten()
        held_piece = -1
        if self.game.hold_piece is not None:
            held_piece = self.game.hold_piece.value
        misc_state = np.array([
            held_piece + 1,
            int(self.game.just_held),
            self.game.level,
            self.game.n_resets,
            self.game.line_count,
            self.game.combo_count + 1,
        ], dtype=np.int32).flatten()
        state = np.concatenate((flat_board, preview_arr, misc_state))
        return state
    def reward(self):
        r = (self.game.score - self.prev_score)
        self.prev_score = self.game.score
        return r
    def is_terminal(self):
        return self.game.is_over

print(check_env(BlockGameEnv()))