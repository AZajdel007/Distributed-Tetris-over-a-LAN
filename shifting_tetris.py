import game as g

class ShiftingTetris(g.Game):
    def game_loop(self):
        pass






def start_shifting_game(screen, bg_color, clock):
    game = ShiftingTetris(screen, bg_color, clock)
    game.gamemode = "Shifting"
    game.lobby()