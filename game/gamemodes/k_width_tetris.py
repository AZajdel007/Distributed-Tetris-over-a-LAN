from game import game as g
import threading


#class KWidthTetris(g.Game):
    #def game_loop(self):
        #print("Start!!!")
        #listening_thread = threading.Thread(target=self.peer.listen)
        #listening_thread.start()



class KWidthTetris(g.Game):
    def __init__(self, screen, bg_color, clock):
        super().__init__(screen, bg_color, clock)
        self.pending_line = None
        self.line_reports = set()


    def _local_full_line(self, row: int) -> None:
        if self.pending_line is not None and self.pending_line != row:
            return

        if self.pending_line is None:
            self.pending_line = row
            self.line_reports = set()

        self.line_reports.add(self.peer.my_ip)
        self.peer.send_msg_to_all_players(f"LINE-{row}")

    def _handle_network_messages(self) -> None:
        while self.peer.received_msg:
            text, sender_ip = self.peer.received_msg.popleft()

            if text.startswith("LINE-"):
                row = int(text.split("-")[1])

                if self.pending_line is None:
                    self.pending_line = row
                    self.line_reports = set()

                if row == self.pending_line:
                    self.line_reports.add(sender_ip)

    def _try_clear_pending_line(self) -> None:
        if self.pending_line is None:
            return

        players = set(self.peer.known_peers.keys()) | {self.peer.my_ip}

        if self.line_reports >= players:
            row = self.pending_line

            del self.grid.grid[row]
            self.grid.grid.insert(0, [0 for _ in range(self.grid.cols)])

            self.pending_line = None
            self.line_reports = set()

    def game_loop(self):
        listening_thread = threading.Thread(target=self.peer.listen, daemon=True)
        listening_thread.start()

        block_goes_down = pg.USEREVENT + 1
        pg.time.set_timer(block_goes_down, 1000)

        clock_start = pg.time.get_ticks()
        game_time_sec = 0

        while self.loop:
            for row in range(self.grid.rows - 1, -1, -1):
                tiles = 0
                for col in range(self.grid.cols):
                    if self.grid.grid[row][col] != 0:
                        tiles += 1

                if tiles == self.grid.cols:
                    self._local_full_line(row)

            self._handle_network_messages()
            self._try_clear_pending_line()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.peer.quit()
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

            if self.current_block.is_placed:
                self.current_block = self.next_block
                if not self.current_block.check_collision_with_wall(0, self.grid):
                    self.next_block = self.random_new_block()
                else:
                    self.loop = False
                    clock_end = pg.time.get_ticks()
                    game_time_sec = (clock_end - clock_start) / 1000

            self.draw()

        self.game_over(self.screen, game_time_sec)



def start_k_width_game(screen, bg_color, clock):
    game = KWidthTetris(screen, bg_color, clock)
    game.gamemode = "K-Width"
    game.lobby()
    game.game_loop()


