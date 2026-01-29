import socket
import time
import threading
import ipaddress
from collections import deque


BROADCAST_IP = "255.255.255.255"
PORT = 5005

class Peer:
    def get_my_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        print(ip)
        return ip

    def get_broadcast_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Pobieramy własne IP
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        finally:
            s.close()


        network = ipaddress.IPv4Network(ip + "/24", strict=False)
        return str(network.broadcast_address)

    def change_ready_status(self):
        if self.my_ready_status:
            self.my_ready_status = False
            for player in self.known_peers.keys():
                self.sock.sendto("Ready:0".encode(), (player, PORT))
        else:
            self.my_ready_status = True
            for player in self.known_peers.keys():
                self.sock.sendto("Ready:1".encode(), (player, PORT))


    def __init__(self, discovery_msg):
        self.my_ready_status = False
        self.discovery_msg = discovery_msg
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(("0.0.0.0", PORT))
        self.my_ip = self.get_my_ip()
        self.my_broadcast = self.get_broadcast_ip()
        self.known_peers = dict()
        self.stop_listen_event = threading.Event()
        self.stop_broadcast_event = threading.Event()
        self.received_msg = deque(maxlen=100)
        self.listen_ignore_list = []
        self.listen_last_msg = None


    def search_for_peers(self):
        self.sock.settimeout(1.0)
        while not self.stop_listen_event.is_set():
            try:
                data, addr = self.sock.recvfrom(1024)
            except socket.timeout:
                continue
            msg = data.decode()
            sender_ip = addr[0]
            print(f"Otrzymano: {sender_ip}: {msg}")
            # ignoruj własne komunikaty
            if sender_ip == self.my_ip:
                continue
            if sender_ip in self.known_peers:
                if msg.startswith("Ready:"):
                    sender_ready_status = bool(int(msg.split(":")[1]))
                    self.known_peers[sender_ip] = sender_ready_status
                elif msg == f"{sender_ip}:QUIT":
                    self.known_peers.pop(sender_ip)
                print(self.known_peers)
                continue

            if msg == self.discovery_msg:
                self.sock.sendto(f"PLAYER_RESPONSE:{self.my_ip}:{self.my_ready_status}".encode(), addr)
                print(f"Wyslano: PLAYER_RESPONSE:{self.my_ip}:{self.my_ready_status} do {sender_ip}")

            elif msg.startswith("PLAYER_RESPONSE:"):
                player_ip = msg.split(":")[1]
                player_ready_status = msg.split(":")[2]
                if player_ip == self.my_ip:
                    continue
                if player_ip not in self.known_peers:
                    self.known_peers[player_ip] = player_ready_status
                    self.sock.sendto(f"PLAYER_RESPONSE:{self.my_ip}:{self.my_ready_status}".encode(), addr)
                print(self.known_peers)

    def broadcast(self):
        while not self.stop_broadcast_event.is_set():
            self.sock.sendto(self.discovery_msg.encode(), (self.my_broadcast, PORT))


            time.sleep(2)

    def send_msg_to_all_players(self, msg):
        if len(self.known_peers) != 0:
            for player in self.known_peers:
                self.sock.sendto(msg.encode(), (player, PORT))

    def send_msg_to_one_player(self, player_ip, msg):
            self.sock.sendto(msg.encode(), (player_ip, PORT))

    def listen(self):
        self.stop_listen_event.clear()
        self.sock.settimeout(1.0)
        #last_msg = None
        while not self.stop_listen_event.is_set():
            try:
                data, sender = self.sock.recvfrom(1024)
                print(f"Otrzymano: {data}:{sender}")
                if sender[0] in self.known_peers:
                    msg = [data.decode(), sender[0]]
                    if msg == "READY TO SHIFT!" or msg == "GO!":
                        self.received_msg.append(msg)
                        print(self.received_msg)

                    #if msg != self.listen_last_msg and '-' in msg[0]:
                    if msg != self.listen_last_msg:
                        self.listen_last_msg = msg
                        if msg[0].split('-')[0] not in self.listen_ignore_list:
                            if msg not in self.received_msg:
                                self.received_msg.append(msg)
                                print(self.received_msg)
                    else:
                        self.received_msg.append(msg)
                        #print(self.received_msg)
            except socket.timeout:
                continue


    def quit(self):
        print(f"{self.my_ip}: Bye")
        for player in self.known_peers:
            self.sock.sendto("Bye".encode(), (player, PORT))

