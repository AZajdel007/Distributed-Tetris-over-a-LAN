import game as g
import threading
import pygame as pg
import sys

class KWidthTetris(g.Game):
    def __init__(self, screen, bg_color, clock):
        super().__init__(screen, bg_color, clock)
        self.known_peers = []
        self.players_row_status = None

        self.known_peers = []

    def even_start(self):
        ready_players = [0 for n in range(len(self.peer.known_peers))]

        loop = True
        while loop:
            self.peer.send_msg_to_all_players("READY!")
            if len(self.peer.received_msg) != 0:
                new_msg = self.peer.received_msg.pop()
                msg, sender_ip = new_msg
                if msg == "READY!":
                    peer_index = self.known_peers.index(sender_ip)
                    ready_players[peer_index] = 1
                    if all(x == 1 for x in ready_players):
                        loop = False




    def game_loop(self):
        print("Start!!!")
        listening_thread = threading.Thread(target=self.peer.listen)
        listening_thread.start()

        block_goes_down = pg.USEREVENT + 1

        self.players_row_status = [[0 for n in range(len(self.peer.known_peers)+1)] for n in range(20)]

        for peer in self.peer.known_peers:
            self.known_peers.append(peer)
        print(self.known_peers)

        # Ustawiamy timer co 1000 ms (czyli co 1 sekundę)
        pg.time.set_timer(block_goes_down, 1000)

        self.even_start()
        self.peer.received_msg.clear()

        clock_start = pg.time.get_ticks()
        game_time_sec = 0
        while self.loop:
            #print(self.players_row_status)
            """for row in range(self.grid.rows - 1, -1, -1):
                tiles = 0
                for col in range(self.grid.cols):
                    if self.grid.grid[row][col] != 0:
                        tiles = tiles + 1
                if tiles == 10:
                    self.players_row_status[row][len(self.peer.known_peers)] = 1
                    self.peer.send_msg_to_all_players(f"{row}-Full")
                    #del self.grid.grid[row]
                    #self.grid.grid.insert(0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                    if all(x == 1 for x in self.players_row_status[row]):
                        for x in range(len(self.peer.known_peers) + 1):
                            self.peer.listen_ignore_list.append(row)
                            self.peer.received_msg.clear()
                            del self.players_row_status[row]
                            self.players_row_status.insert(0, [0 for n in range(len(self.peer.known_peers)+1)])
                            del self.grid.grid[row]
                            self.grid.grid.insert(0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                            self.peer.send_msg_to_all_players(f"{row}-Cleared")
                            self.peer.listen_ignore_list.remove(row)
            """
            if self.current_block.is_placed:
                self.current_block = self.next_block
                if not self.current_block.check_collision_with_wall(0, self.grid):
                    for row in range(self.grid.rows - 1, -1, -1):
                        tiles = 0
                        for col in range(self.grid.cols):
                            if self.grid.grid[row][col] != 0:
                                tiles = tiles + 1
                        if tiles == 10:
                            self.players_row_status[row][len(self.peer.known_peers)] = 1
                            self.peer.send_msg_to_all_players(f"{row}-Full")
                            # del self.grid.grid[row]
                            # self.grid.grid.insert(0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                            if all(x == 1 for x in self.players_row_status[row]):
                                self.peer.listen_ignore_list.append(row)
                                self.peer.received_msg.clear()
                                del self.players_row_status[row]
                                self.players_row_status.insert(0, [0 for n in range(len(self.peer.known_peers) + 1)])
                                del self.grid.grid[row]
                                self.grid.grid.insert(0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                                self.peer.send_msg_to_all_players(f"{row}-Cleared")
                                self.peer.listen_ignore_list.remove(row)
                    self.next_block = self.random_new_block()
                else:
                    self.loop = False
                    self.peer.send_msg_to_all_players("RIP")
                    clock_end = pg.time.get_ticks()
                    game_time_sec = (clock_end - clock_start) / 1000
                    self.peer.quit()
                    self.peer.stop_listen_event.set()
                    self.peer.stop_broadcast_event.set()
                    listening_thread.join()

            if len(self.peer.received_msg) != 0:
                print("elo")
                new_msg = self.peer.received_msg.pop()
                new_msg, sender_ip = new_msg
                print(self.players_row_status)

                if '-' in new_msg:
                    row, row_status = new_msg.split('-')
                    row = int(row)
                    if row_status == "Full":
                        # obsługa informacji że gracz ma pełny jeden wiersz
                        peer_index = self.known_peers.index(sender_ip)
                        self.players_row_status[row][peer_index] = 1
                        print(peer_index)
                        for player in range(len(self.known_peers) + 1):
                            if all(x == 1 for x in self.players_row_status[row]):
                                for x in range(len(self.known_peers) + 1):
                                    del self.players_row_status[row]
                                    self.players_row_status.insert(0,
                                                                   [0 for n in range(len(self.peer.known_peers) + 1)])
                                    del self.grid.grid[row]
                                    self.grid.grid.insert(0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                                    self.peer.send_msg_to_all_players(f"{row}-Cleared")
                    else:
                        # obsługa informacji że gracz skasował jeden wiersz
                        peer_index = self.known_peers.index(sender_ip)
                        self.players_row_status[row][peer_index] = 0
                        print(peer_index)

                elif "RIP" in new_msg:
                    self.loop = False
                    clock_end = pg.time.get_ticks()
                    game_time_sec = (clock_end - clock_start) / 1000
                    self.peer.quit()
                    self.peer.stop_listen_event.set()
                    self.peer.stop_broadcast_event.set()
                    listening_thread.join()
                    del self.peer
                elif "Bye" in new_msg:
                    self.loop = False
                    clock_end = pg.time.get_ticks()
                    game_time_sec = (clock_end - clock_start) / 1000
                    self.peer.quit()
                    self.peer.stop_listen_event.set()
                    self.peer.stop_broadcast_event.set()
                    listening_thread.join()
                    del self.peer

                print(self.players_row_status)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.peer.send_msg_to_all_players("Bye")
                    self.peer.quit()
                    self.peer.stop_listen_event.set()
                    self.peer.stop_broadcast_event.set()
                    listening_thread.join()
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



            self.draw()
        self.game_over(self.screen, game_time_sec)


def start_k_width_game(screen, bg_color, clock):
    game = KWidthTetris(screen, bg_color, clock)
    game.gamemode = "K-Width"
    game.lobby()
    game.game_loop()
    del game
