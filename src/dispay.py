import pygame as pg
from block_game import BlockGame, input_t, std_piece_set, dot_piece_set
import random

CELL_SIZE = 25
TICK_RATE = 60

def gen_dot_board(n = 15, width = 10, height = 20):
    board = [[0 for _ in range(width)] for _ in range(height)]
    for r in range(height)[:-(n+1):-1]:
        empty = random.randint(0, width-1)
        for c in range(width):
            if c != empty:
                board[r][c] = 1
    return board

class control_handler:
    def __init__(self, key_list, input_delay) -> None:
        self.input_delay = input_delay
        self.key_set = set(key_list)
        self.key_pressed_map = dict((keys, False) for keys in self.key_set)
        self.input_delay_map = dict((keys, 0) for keys in self.key_set)

    def register_keys(self, key_list):
        for key in key_list:
            if key not in self.key_set:
                self.key_set.add(key)
                self.key_pressed_map[key] = False
                self.input_delay_map[key] = 0

    def detect_key_press(self, event_list):
        for event in event_list:
            if event.type == pg.KEYUP and event.key in self.key_set:
                self.key_pressed_map[event.key] = False
        for event in event_list:
            if event.type == pg.KEYDOWN and event.key in self.key_set:
                self.key_pressed_map[event.key] = True
                self.input_delay_map[event.key] = 0
        for key in self.key_set:
            if self.input_delay_map[key] > 0:
                self.input_delay_map[key] -= 1

    def get_pressed_keys(self):
        pressed = [key for key in self.key_pressed_map if self.key_pressed_map[key]]
        allowed = [key for key in pressed if self.input_delay_map[key] == 0]
        for key in allowed:
            self.input_delay_map[key] = self.input_delay
        return allowed

    def is_key_pressed(self, key):
        if key not in self.key_pressed_map:
            return False
        return self.key_pressed_map[key]

def main():
    pg.init()
    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()
    game = BlockGame(1)
    controls = control_handler([
        pg.K_LEFT, pg.K_RIGHT, pg.K_DOWN,
        pg.K_z, pg.K_x, pg.K_SPACE,
        pg.K_c
    ], 15)
    while True:
        # input
        event_list = pg.event.get()
        for event in event_list:
            if event.type == pg.QUIT:
                pg.quit()
                exit(0)
        controls.detect_key_press(event_list)
        for key in controls.get_pressed_keys():
            match key:
                case pg.K_LEFT:
                    game.set_input(input_t.LEFT)
                case pg.K_RIGHT:
                    game.set_input(input_t.RIGHT)
                case pg.K_DOWN:
                    print('soft drop')
                    game.set_input(input_t.SOFT_DROP)
                case pg.K_z:
                    game.set_input(input_t.ROTATE_LEFT)
                case pg.K_x:
                    game.set_input(input_t.ROTATE_RIGHT)
                case pg.K_SPACE:
                    game.set_input(input_t.HARD_DROP)
                case pg.K_c:
                    game.set_input(input_t.HOLD)
        # update game state
        if game.is_over:
            exit(0)
        if game.is_full_clear:
            print('you win')
            exit(0)
        game.update_state()

        # render
        screen.fill((0, 0, 0))
        grid_width = game.width * CELL_SIZE
        grid_height = game.height * CELL_SIZE
        grid_x = (screen.get_width() - grid_width) // 2
        grid_y = (screen.get_height() - grid_height) // 2
        board = game.get_visible_board()
        for y in range(game.height):
            for x in range(game.width):
                rect = pg.Rect(grid_x + x * CELL_SIZE, grid_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if board[y][x].state == 1:
                    pg.draw.rect(screen, "white", rect)
                elif board[y][x].state == 2:
                    pg.draw.rect(screen, "red", rect)
                else:
                    pg.draw.rect(screen, "white", rect, 1)
        #print(game)
        pg.display.flip()
        clock.tick(TICK_RATE)

if __name__ == '__main__':
    main()