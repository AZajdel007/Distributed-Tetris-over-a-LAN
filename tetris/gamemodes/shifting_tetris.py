from tetris import game as g
import threading
import pygame as pg
import ipaddress
import sys
from commons import colors

class ShiftingTetris(g.Game):
    def __init__(self, screen, bg_color, clock):
        super().__init__(screen, bg_color, clock)
        self.known_peers = []
        self.till_next_shift = 0
        self.shift_event = None
        self.next_player = None
        self.players_ready_for_shift = []
        self.next_shift = 0
    def set_next_player(self):
        all_players = self.known_peers.copy()
        all_players.append(self.peer.my_ip)
        print(all_players)
        all_players.sort(key=ipaddress.ip_address)
        for i, ip in enumerate(all_players):
            if ip == self.peer.my_ip:
                if i == len(all_players) - 1:
                    self.next_player = all_players[0]
                else:
                    self.next_player = all_players[i+1]
                break
        print(self.next_player)

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





    def draw(self):
        self.screen.fill(self.background_color)
        self.grid.draw(self.screen)

        self.current_block.draw(self.screen)

        tile_rect = pg.Rect(self.shift + 25 + 300, 75 , 0.75*self.shift, 125)
        pg.draw.rect(self.screen, colors.color[9], tile_rect)
        self.next_block.next_block_draw(self.screen)

        tile_rect2 = pg.Rect(25, 75, 0.75 * self.shift, 125)
        pg.draw.rect(self.screen, colors.color[9], tile_rect2)
        self.next_block.next_block_draw(self.screen)

        font = pg.font.Font(None, 36)
        font2 = pg.font.Font(None, 50)
        text_surf = font.render("Next piece:", True, colors.color[10])
        self.screen.blit(text_surf, (self.shift + 35 + 300, 25))
        self.till_next_shift = int(self.till_next_shift / 1000)
        text_surface = font.render(f"Next shift:", True, (255, 255, 255))
        text_surface2 = font2.render(f"{self.till_next_shift}", True, (255, 255, 255))

        # wyświetl na ekranie
        self.screen.blit(text_surface, (40, 30))
        self.screen.blit(text_surface2, (85, 120))
        pg.display.update()
        self.clock.tick(60)


    def shift_action(self):
        last_column = [row[-1] for row in self.grid.grid]
        msg_for_next_player = ""
        for i, col in enumerate(last_column):
            msg_for_next_player = msg_for_next_player + str(col) + ","

        self.peer.send_msg_to_all_players("READY TO SHIFT!")
        while len(self.players_ready_for_shift) != len(self.peer.known_peers):
            if len(self.peer.received_msg) != 0:
                new_msg = self.peer.received_msg.pop()
                new_msg, sender_ip = new_msg
                if "," in new_msg:
                    col = new_msg.split(',')
                    col.remove('')
                    for i, val in enumerate(col):
                        col[i] = int(val)
                    print(f"col: {col}")
                    print(type(col[0]))
                    self.next_shift = col
                elif new_msg.startswith("READY TO SHIFT!"):
                    self.players_ready_for_shift.append(sender_ip)
        self.peer.send_msg_to_one_player(self.next_player, msg_for_next_player)


        loop = True
        if self.next_shift != 0:
            for i, row in enumerate(self.grid.grid):
                row.pop()
                row.insert(0, self.next_shift[i])
            loop = False

        while loop:
            if len(self.peer.received_msg) != 0:
                new_msg = self.peer.received_msg.pop()
                new_msg, sender_ip = new_msg
                if ',' in new_msg:
                    col = new_msg.split(',')
                    col.remove('')
                    for i, val in enumerate(col):
                        col[i] = int(val)
                    print(f"col: {col}")
                    print(type(col[0]))

                    for i, row in enumerate(self.grid.grid):
                        row.pop()
                        row.insert(0, col[i])
                    loop = False
        self.next_shift = 0
        self.players_ready_for_shift.clear()
        pg.time.set_timer(self.shift_event, 0)
        pg.time.set_timer(self.shift_event, 15000)



    def game_loop(self):
        print("Start!!!")
        listening_thread = threading.Thread(target=self.peer.listen)
        listening_thread.start()

        block_goes_down = pg.USEREVENT + 1
        self.shift_event = pg.USEREVENT + 2


        for peer in self.peer.known_peers:
            self.known_peers.append(peer)
        self.set_next_player()
        print(self.known_peers)

        # Ustawiamy timer co 1000 ms
        pg.time.set_timer(block_goes_down, 1000)
        pg.time.set_timer(self.shift_event, 15000)
        self.even_start()
        self.peer.received_msg.clear()
        self.peer.listen_last_msg = None

        clock_start = pg.time.get_ticks()
        game_time_sec = 0
        last_shift = pg.time.get_ticks()
        while self.loop:
            now = pg.time.get_ticks()
            self.till_next_shift = 15000 - (now - last_shift)
            self.till_next_shift = max(0, self.till_next_shift)

            if self.current_block.is_placed:
                self.current_block = self.next_block
                if not self.current_block.check_collision_with_wall(0, self.grid):
                    for row in range(self.grid.rows - 1, -1, -1):
                        tiles = 0
                        for col in range(self.grid.cols):
                            if self.grid.grid[row][col] != 0:
                                tiles = tiles + 1
                        if tiles == 10:
                            del self.grid.grid[row]
                            self.grid.grid.insert(0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
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
                new_msg = self.peer.received_msg.pop()
                new_msg, sender_ip = new_msg



                if "," in new_msg:
                    col = new_msg.split(',')
                    col.remove('')
                    for i, val in enumerate(col):
                        col[i] = int(val)
                    print(f"col: {col}")
                    print(type(col[0]))
                    self.next_shift = col
                elif "READY TO SHIFT!" in new_msg:
                    if sender_ip != self.peer.my_ip and sender_ip not in self.players_ready_for_shift:
                        self.players_ready_for_shift.append(sender_ip)
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
                elif event.type == self.shift_event:
                    last_shift = pg.time.get_ticks()
                    self.shift_action()
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


def start_shifting_game(screen, bg_color, clock):
    game = ShiftingTetris(screen, bg_color, clock)
    game.gamemode = "Shifting"
    game.lobby()
    game.game_loop()
    del game