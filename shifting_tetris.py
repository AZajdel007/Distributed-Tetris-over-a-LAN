import game as g
import pygame as pg
import sys

timeBetweenShifts = 30 #how many seconds
#jeżeli gra przegrana bye(wyrzucenie z gry)
class ShiftingTetris(g.Game):
    def shift(self):
        #send out data
        # known peers is ip and status
        global msg
        tmp = self.peer.known_peers.keys()
        tmp=list(tmp)
        tmp.append(self.peer.my_ip)
        tmp.sort()

        if self.peer.my_ip == tmp[-1]: next_player=tmp[0]
        else: next_player = tmp[self.peer.my_ip + 1]

        for row in range(self.grid.rows):
            msg = msg.join(self.grid.cols[0].rows[row])

        self.peer.send_msg_to_one_player(self,next_player,msg)

        str_msg = self.peer.recived_msg.pop()[0]

        for col in range(self.grid.cols): # 20 rows, 10 columns
            for row in range(self.grid.rows):
                self.grid[row][col] = self.grid[row][col-1]
                if col==0:
                    self.grid[row][col] = str_msg[col]

        self.grid.draw(self,self.screen)
        pass

    def game_loop(self):

        block_goes_down = pg.USEREVENT + 1
        shift = pg.USEREVENT + 2

        # Ustawiamy timer co 1000 ms (czyli co 1 sekundę)
        pg.time.set_timer(block_goes_down, 1000)
        pg.time.set_timer(shift, timeBetweenShifts*1000) #co 30s wrzuca event shift do queue

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
                    #if self.current_block.check_collision_sides(self.grid):
                    #    self.current_block.put_on_grid(self.grid)
                elif event.type == shift:
                    #kod mechaniki shifting tetrisa
                    self.shift()
                    continue
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
            self.screen.fill(self.background_color)
            self.grid.draw(self.screen)

            self.current_block.draw(self.screen)

            pg.display.update()
            self.clock.tick(60)
        self.game_over(self.screen)




def start_shifting_game(screen, bg_color, clock):
    game = ShiftingTetris(screen, bg_color, clock)
    game.gamemode = "Shifting"
    game.lobby()

