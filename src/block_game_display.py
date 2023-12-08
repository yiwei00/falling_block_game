import pygame as pg
from block_game import BlockGame, action_t

CELL_SIZE = 25
TICK_RATE = 60

def main():
    pg.init()
    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()
    game = BlockGame(1, rand_board=True)
    while True:
        # input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit(0)
            if event.type == pg.KEYDOWN:
                match event.key:
                    case pg.K_LEFT:
                        game.set_action(action_t.LEFT)
                    case pg.K_RIGHT:
                        game.set_action(action_t.RIGHT)
                    case pg.K_DOWN:
                        game.set_action(action_t.SOFT_DROP)
                    case pg.K_z:
                        game.set_action(action_t.ROTATE_LEFT)
                    case pg.K_x:
                        game.set_action(action_t.ROTATE_RIGHT)
                    case pg.K_SPACE:
                        game.set_action(action_t.HARD_DROP)
                    case pg.K_c:
                        game.set_action(action_t.HOLD)

        # update game state
        if game.is_over:
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
        print(game.score, game.level)
        pg.display.flip()
        clock.tick(TICK_RATE)

if __name__ == '__main__':
    main()