import game as g
import threading
import pygame as pg
import sys
import queue

class KWidthTetris(g.Game):
    def __init__(self, screen, bg_color, clock):
        super().__init__(screen, bg_color, clock)
        self.players_row_status = None

    def game_loop(self):
        print("Start!!!")
        listening_thread = threading.Thread(target=self.peer.listen)
        listening_thread.start()

        block_goes_down = pg.USEREVENT + 1

        self.players_row_status = [[0 for n in range(len(self.peer.known_peers)+1)] for n in range(20)]

        # Ustawiamy timer co 1000 ms (czyli co 1 sekundę)
        pg.time.set_timer(block_goes_down, 1000)
        while self.loop:
            print(self.players_row_status)
            for row in range(self.grid.rows - 1, -1, -1):
                tiles = 0
                for col in range(self.grid.cols):
                    if self.grid.grid[row][col] != 0:
                        tiles = tiles + 1
                if tiles == 10:
                    self.players_row_status[row][len(self.peer.known_peers)] = 1
                    self.peer.send_msg_to_all_players(f"{self.peer.my_ip}:{row}")
                    #del self.grid.grid[row]
                    #self.grid.grid.insert(0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                    if all(x == 1 for x in self.players_row_status[row]):
                        for x in range(len(self.peer.known_peers) + 1):
                            self.players_row_status[row][x] = 0
                            del self.grid.grid[row]
                            self.grid.grid.insert(row, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

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
                        self.current_block.drop(self.grid)
                elif not self.peer.received_msg.empty():
                    new_msg = self.peer.received_msg.get()
                    print(self.players_row_status)
                    if ':' in new_msg:
                        sender_ip, row = new_msg.split(":")
                        peer_index = self.peer.known_peers.index(sender_ip)
                        self.players_row_status[row][peer_index] = 1
                        for player in range(len(self.peer.known_peers)+1):
                            if all(x == 1 for x in self.players_row_status[row]):
                                for x in range(len(self.peer.known_peers)+1):
                                    self.players_row_status[row][x] = 0
                                    del self.grid.grid[row]
                                    self.grid.grid.insert(row, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])


            self.screen.fill(self.background_color)
            self.grid.draw(self.screen)

            self.current_block.draw(self.screen)

            pg.display.update()
            self.clock.tick(60)
        self.game_over(self.screen)


def start_k_width_game(screen, bg_color, clock):
    game = KWidthTetris(screen, bg_color, clock)
    game.gamemode = "K-Width"
    game.lobby()
    game.game_loop()

"""
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

"""
