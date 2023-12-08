import numpy as np
from block_game import *
from gymnasium import Env, spaces
import gymnasium
from stable_baselines3.common.env_checker import check_env
import pygame as pg

CELL_SIZE = 25
TICK_RATE = 20

def piece2num(piece):
    return piece.value

def num2act(num):
    return action_t(num)

def gen_dot_board(n = 15, width = 10, height = 20):
    board = [[0 for _ in range(width)] for _ in range(height)]
    for r in range(height)[:-(n+1):-1]:
        empty = random.randint(0, width-1)
        for c in range(width):
            if c != empty:
                board[r][c] = 1
    return board

class BlockGameEnv(Env):
    def __init__(self, n_preview=5, line_limit=150, set_speed = None, dot_game = False):
        self.n_preview = n_preview if not dot_game else 1
        self.game_args = {
            'line_limit': line_limit,
            'set_speed': set_speed,
            'starting_board': None,
            'piece_subset': std_piece_set,
        }
        if dot_game:
            self.game_args['piece_subset'] = dot_piece_set
            self.game_args['starting_board'] = gen_dot_board()
        self.prev_score = 0
        self.game = BlockGame(
            **self.game_args
        )

        board_size = self.game.width * self.game.height
        board_space = [3] * board_size
        preview_space = [len(piece_t)] * self.n_preview
        # hold piece (int), just held (bool), level (int), n resets (int), line count (int), combo count (int)
        misc_space = [len(piece_t) + 1, 2, line_limit//10 + 2, 16, line_limit + 1, line_limit + 2]

        self.action_space = spaces.Discrete(len(action_t))
        self.observation_space = spaces.MultiDiscrete(board_space + preview_space + misc_space)


    def reset(self, seed = None):
        self.game = BlockGame(
            seed = seed,
            **self.game_args
        )
        self.prev_score = 0
        state = self.get_state()
        return state, {}

    def step(self, action):
        self.game.set_action(num2act(action))
        self.game.update_state()
        new_score = self.game.score
        reward = new_score - self.prev_score
        self.prev_score = new_score
        return self.get_state(), reward, self.game.is_over or self.game.is_full_clear, False, {}

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
        if self.game.is_over:
            r -= 10_000
        return r

    def render(self, mode='human'):
        if mode != 'human':
            return
        print(self.game)

    def close(self):
        pg.quit()
        exit(0)

print(check_env(BlockGameEnv()))

gymnasium.register(
    id='BlockGame-v0',
    entry_point='env:BlockGameEnv',
    kwargs={
        'n_preview': 5,
        'line_limit': 150,
        'set_speed': None,
        'dot_game': False
    }
)