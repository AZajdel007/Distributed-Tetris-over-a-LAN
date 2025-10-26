import game as g
import threading
import queue

class KWidthTetris(g.Game):
    def game_loop(self):
        print("Start!!!")
        listening_thread = threading.Thread(target=self.peer.listen)
        listening_thread.start()





def start_k_width_game(screen, bg_color, clock):
    game = KWidthTetris(screen, bg_color, clock)
    game.gamemode = "K-Width"
    game.lobby()
    game.game_loop()