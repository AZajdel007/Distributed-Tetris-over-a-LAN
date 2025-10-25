import pygame as pg
import game
import button
import colors
from functools import partial
import sys

class MainMenu:
    def __init__(self):
        self.screen = pg.display.set_mode((300, 600))
        self.background_color = (1, 8, 59)
        pg.display.set_caption("Tetris")
        self.clock = pg.time.Clock()

    def main_menu(self):
        loop = True
        image = pg.image.load("assets/logo.png").convert_alpha()
        self.screen.fill(self.background_color)
        start_solo_game_action = partial(game.start_solo_game, self.screen, self.background_color, self.clock)
        start_k_width_action = partial(game.start_k_width_game, self.screen, self.background_color, self.clock)
        start_shifting_action = partial(game.start_shifting_game, self.screen, self.background_color, self.clock)

        play_solo_button = button.Button(50, 300, 200, 50, "Play Solo", colors.color[8], colors.color[9], colors.color[0], start_solo_game_action)
        play_k_width_button = button.Button(50, 400, 200, 50, "Play K-Width", colors.color[8], colors.color[9], colors.color[0], start_k_width_action)
        play_shifting_button = button.Button(50, 500, 200, 50, "Play Shifting", colors.color[8], colors.color[9], colors.color[0], start_shifting_action)


        while loop:
            self.screen.fill(self.background_color)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                play_solo_button.handle_event(event)
                play_k_width_button.handle_event(event)
                play_shifting_button.handle_event(event)
            self.screen.blit(image, (25, 50))
            play_solo_button.draw(self.screen)
            play_k_width_button.draw(self.screen)
            play_shifting_button.draw(self.screen)
            pg.display.flip()