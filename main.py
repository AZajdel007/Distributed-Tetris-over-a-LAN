import pygame
import pygame as pg
import sys
import grid
import blocks
import colors
pg.init()
background_color = (1, 8, 59)

grid = grid.Grid()
screen = pg.display.set_mode((300, 600))
pygame.display.set_caption("Tetris")
clock = pg.time.Clock()

loop = True


grid.grid[3][1] = 1



block = blocks.IBlock()
print(grid.grid)
while loop:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                block.move_x(-1, grid)
            elif event.key == pygame.K_RIGHT:
                block.move_x(1, grid)
            elif event.key == pygame.K_UP:
                block.rotate(grid)
    screen.fill(background_color)
    grid.draw(screen)

    block.draw(screen)

    pg.display.update()
    clock.tick(60)