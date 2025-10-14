from asyncio import wait_for
import colors
import grid
import random
import blocks
import pygame as pg
import sys


def is_cursor_over(rect):
    return rect.collidepoint(pg.mouse.get_pos())

class Game:

    def main_menu(self):
        loop = True
        self.screen.fill(self.background_color)
        while loop:
            play_solo_button = pg.Rect(50, 50, 100, 50)
            play_k_width_button = pg.Rect(50, 200, 100, 50)
            play_shifting_button = pg.Rect(50, 300, 100, 50)

            cursor_over_play_solo_button = is_cursor_over(play_solo_button)
            cursor_over_play_k_width_button = is_cursor_over(play_k_width_button)
            cursor_over_play_shifting_button = is_cursor_over(play_shifting_button)

            solo_button_color = colors.color[1] if cursor_over_play_solo_button else colors.color[2]
            k_width_button_color = colors.color[1] if cursor_over_play_k_width_button else colors.color[2]
            shifting_button_color = colors.color[1] if cursor_over_play_shifting_button else colors.color[2]

            pg.draw.rect(self.screen, solo_button_color, play_solo_button)
            pg.draw.rect(self.screen, k_width_button_color, play_k_width_button)
            pg.draw.rect(self.screen, shifting_button_color, play_shifting_button)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if cursor_over_play_solo_button:
                        print("Solo")
                    elif cursor_over_play_k_width_button:
                        print("k-width")
                    elif cursor_over_play_shifting_button:
                        print("Shifting")
            pg.display.flip()

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

        pg.init()
        self.screen = pg.display.set_mode((300, 600))
        self.background_color = (1, 8, 59)

        pg.display.set_caption("Tetris")
        self.clock = pg.time.Clock()

    def game_over(self, screen):
        for n in range(0, 5):
            self.grid.draw(screen)
            pg.display.update()
            pg.time.wait(300)
            self.current_block.draw(screen)
            pg.display.update()
            pg.time.wait(300)




    def game_loop(self):


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
            self.screen.fill(self.background_color)
            self.grid.draw(self.screen)

            self.current_block.draw(self.screen)

            pg.display.update()
            self.clock.tick(60)
        self.game_over(self.screen)



game = Game()
game.main_menu()
#game.game_loop()