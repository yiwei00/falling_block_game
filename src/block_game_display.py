import pygame as pg
from block_game import BlockGame, Piece

CELL_SIZE = 25

def main():
    pg.init()
    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()
    game = BlockGame()
    game.drop_piece(Piece.J)
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit(0)
        screen.fill((0, 0, 0))
        grid_width = game.width * CELL_SIZE
        grid_height = game.height * CELL_SIZE
        grid_x = (screen.get_width() - grid_width) // 2
        grid_y = (screen.get_height() - grid_height) // 2
        for y in range(game.height):
            for x in range(game.width):
                rect = pg.Rect(grid_x + x * CELL_SIZE, grid_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if game.board[y + 2][x].state == 1:
                    pg.draw.rect(screen, "white", rect)
                elif game.board[y + 2][x].state == 2:
                    pg.draw.rect(screen, "red", rect)
                else:
                    pg.draw.rect(screen, "white", rect, 1)
        pg.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()