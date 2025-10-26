import game as g

class KWidthTetris(g.Game):
    def game_loop(self):
        print("Start!!!")




def start_k_width_game(screen, bg_color, clock):
    game = KWidthTetris(screen, bg_color, clock)
    game.gamemode = "K-Width"
    game.lobby()