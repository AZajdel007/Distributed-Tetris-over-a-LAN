import grid
import random
import blocks
import pygame as pg
import sys
import lan_connection as lan
import threading
import colors
import button
import time


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

    def __init__(self, screen, bg_color, clock):
        self.grid = grid.Grid()
        self.loop = True
        self.current_block = self.random_new_block()
        self.next_block = self.random_new_block()
        self.gamemode = "Tetris"
        self.peer = None

        self.shift = 200
        self.screen = screen
        self.background_color = bg_color
        self.clock = clock

    def game_over_screen(self, game_time):
        self.screen.fill(self.background_color)
        font = pg.font.Font(None, 36)
        text_surf = font.render(f"You have last: {game_time}", True, colors.color[10])
        self.screen.blit(text_surf, (24, 25))
        pg.display.update()
        self.clock.tick(60)
        pg.time.wait(3000)






    def game_over(self, screen, game_time_sec):
        for n in range(0, 5):
            self.grid.draw(screen)
            pg.display.update()
            pg.time.wait(300)
            self.current_block.draw(screen)
            pg.display.update()
            pg.time.wait(300)

        self.game_over_screen(game_time_sec)


    def lobby(self):
        self.peer = lan.Peer(self.gamemode)
        listening_thread = threading.Thread(target=self.peer.search_for_peers)
        broadcast_thread = threading.Thread(target=self.peer.broadcast)
        listening_thread.start()
        broadcast_thread.start()
        lobby_loop = True

        change_ready_status_button = button.Button(self.shift+50, 300, 200, 50, "Ready!", colors.color[8], colors.color[9],
                                         colors.color[0], self.peer.change_ready_status)

        while lobby_loop:
            self.screen.fill(self.background_color)
            font = pg.font.Font(None, 36)
            text_surf = font.render("Searching for players", True, colors.color[10])
            self.screen.blit(text_surf, (self.shift+24, 25))


            if self.peer.my_ready_status:
                change_ready_status_button.text = "Not ready"
                text_surf = font.render("Ready!", True, colors.color[11])
                self.screen.blit(text_surf, (self.shift+100, 75))
            else:
                change_ready_status_button.text = "Ready!"
                text_surf = font.render("Not ready!", True, colors.color[12])
                self.screen.blit(text_surf, (self.shift+86, 75))

            ready_peers = 0
            for known_peer in self.peer.known_peers.keys():
                if str(self.peer.known_peers[known_peer]) == 'True':
                    ready_peers += 1
            if ready_peers == len(self.peer.known_peers) and ready_peers != 0 and self.peer.my_ready_status == True:
                lobby_loop = False
                self.peer.stop_listen_event.set()
                self.peer.stop_broadcast_event.set()
                listening_thread.join()
                broadcast_thread.join()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.peer.quit()
                    self.peer.stop_listen_event.set()
                    self.peer.stop_broadcast_event.set()
                    listening_thread.join()
                    broadcast_thread.join()
                    pg.quit()
                    sys.exit()


                change_ready_status_button.handle_event(event)

            change_ready_status_button.draw(self.screen)
            pg.display.update()
            self.clock.tick(60)


    def game_loop(self):
        pass

    def draw(self):
        self.screen.fill(self.background_color)
        self.grid.draw(self.screen)

        self.current_block.draw(self.screen)

        tile_rect = pg.Rect(self.shift + 25 + 300, 75 , 0.75*self.shift, 125)
        pg.draw.rect(self.screen, colors.color[9], tile_rect)
        self.next_block.next_block_draw(self.screen)

        font = pg.font.Font(None, 36)
        text_surf = font.render("Next piece:", True, colors.color[10])
        self.screen.blit(text_surf, (self.shift + 35 + 300, 25))

        pg.display.update()
        self.clock.tick(60)


class SoloTetris(Game):
    def game_loop(self):
        block_goes_down = pg.USEREVENT + 1

        # Ustawiamy timer co 1000 ms (czyli co 1 sekundę)
        pg.time.set_timer(block_goes_down, 1000)

        clock_start = pg.time.get_ticks()
        game_time_sec = 0
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
                    clock_end = pg.time.get_ticks()
                    game_time_sec = (clock_end - clock_start) / 1000

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
            self.draw()
        self.game_over(self.screen, game_time_sec)






def start_solo_game(screen, bg_color, clock):
    game = SoloTetris(screen, bg_color, clock)
    game.game_loop()

def start_k_width_game():
    pass


