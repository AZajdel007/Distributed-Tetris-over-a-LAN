import grid
import random
import blocks
import pygame as pg
import sys
class Game:
    def random_new_block(self):
        block_id = random.randint(1, 8)
        if block_id == 1:
            return blocks.IBlock()
        elif block_id == 2:
            return blocks.OBlock()
        elif block_id == 3:
            return blocks.JBlock()
        elif block_id == 4:
            return blocks.LBlock()
        elif block_id == 5:
            return blocks.SBlock()
        elif block_id == 6:
            return blocks.TBlock()
        elif block_id == 7:
            return blocks.ZBlock()
        else:
            return blocks.TBlock()

    def __init__(self):
        self.grid = grid.Grid()
        self.loop = True
        self.current_block = self.random_new_block()
        self.next_block = self.random_new_block()




    def game_loop(self):
        pg.init()
        background_color = (1, 8, 59)

        screen = pg.display.set_mode((300, 600))
        pg.display.set_caption("Tetris")
        clock = pg.time.Clock()
        block_goes_down = pg.USEREVENT + 1

        # Ustawiamy timer co 1000 ms (czyli co 1 sekundę)
        pg.time.set_timer(block_goes_down, 1000)
        while self.loop:
            for row in range(self.grid.rows - 1, -1, -1):
                tiles = 0
                for col in range(self.grid.cols):
                    if self.grid.grid[row][col] != 0:
                        tiles = tiles + 1
                if tiles == 10:
                    del self.grid.grid[row]
                    self.grid.grid.insert(0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])


            if self.current_block.is_placed:
                self.current_block = self.next_block
                if not self.current_block.check_collision_with_wall(0, self.grid):
                    self.next_block = self.random_new_block()
                else:
                    self.loop = False


            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == block_goes_down:
                    self.current_block.move_down(self.grid)
                    if self.current_block.check_collision_under(self.grid):
                        self.current_block.put_on_grid(self.grid)
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        self.current_block.move_x(-1, self.grid)
                    elif event.key == pg.K_RIGHT:
                        self.current_block.move_x(1, self.grid)
                    elif event.key == pg.K_UP:
                        self.current_block.rotate(self.grid)
                    elif event.key == pg.K_DOWN:
                        self.current_block.move_down(self.grid)
                    elif event.key == pg.K_SPACE:
                        self.current_block.put_on_grid(self.grid)
            screen.fill(background_color)
            self.grid.draw(screen)

            self.current_block.draw(screen)

            pg.display.update()
            clock.tick(60)

game = Game()
game.game_loop()