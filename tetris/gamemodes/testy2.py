from tetris import game as g
import threading
import pygame as pg
import ipaddress
import sys

class ShiftingTetris(g.Game):
    def __init__(self, screen, bg_color, clock):
        super().__init__(screen, bg_color, clock)
        self.known_peers = []
        self.players_row_status = None

        self.known_peers = []
        self.next_player = None
    def set_next_player(self):
        all_players = self.known_peers + self.peer.my_ip
        print(all_players)
        all_players.sort(key=ipaddress.ip_address)
        for i, ip in enumerate(all_players):
            if ip == self.peer.my_ip:
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


    def game_loop(self):
        print("Start!!!")
        listening_thread = threading.Thread(target=self.peer.listen)
        listening_thread.start()

        block_goes_down = pg.USEREVENT + 1

        self.players_row_status = [[0 for n in range(len(self.peer.known_peers)+1)] for n in range(20)]

        for peer in self.peer.known_peers:
            self.known_peers.append(peer)
        self.set_next_player()
        print(self.known_peers)

        # Ustawiamy timer co 1000 ms (czyli co 1 sekundę)
        pg.time.set_timer(block_goes_down, 1000)

        #self.even_start()

        self.peer.received_msg.clear()
        self.peer.quit()
        self.peer.stop_listen_event.set()
        self.peer.stop_broadcast_event.set()
        listening_thread.join()
        del self.peer


def start_shifting_game(screen, bg_color, clock):
    game = ShiftingTetris(screen, bg_color, clock)
    game.gamemode = "Shifting"
    game.lobby()
    game.game_loop()
    del game