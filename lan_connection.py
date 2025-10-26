import socket
import time
import threading
import ipaddress
import queue


BROADCAST_IP = "255.255.255.255"
PORT = 5005

class Peer:
    def get_my_ip(self):
        """Sprytne pobranie własnego IP"""
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
            # Pobierz własne IP (np. 192.168.1.23)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        finally:
            s.close()

        # Załóż, że masz typową sieć domową /24
        # (jeśli masz inną maskę, możesz ją dobrać dynamicznie)
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
        self.received_msg = queue.Queue()


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
                if player_ip not in self.known_peers:
                    self.known_peers[player_ip] = player_ready_status
                    self.sock.sendto(f"PLAYER_RESPONSE:{self.my_ip}:{self.my_ready_status}".encode(), addr)
                print(self.known_peers)

    def broadcast(self):
        while not self.stop_broadcast_event.is_set():
            self.sock.sendto(self.discovery_msg.encode(), (self.my_broadcast, PORT))


            time.sleep(2)

    def send_msg_to_all_players(self, msg):
        for player in self.known_peers:
            self.sock.sendto(msg.encode(), (player, PORT))

    def send_msg_to_one_player(self, player_ip, msg):
            self.sock.sendto(msg.encode(), (player_ip, PORT))

    def listen(self):
        self.stop_listen_event.clear()
        self.sock.settimeout(1.0)
        while not self.stop_listen_event.is_set():
            try:
                data, addr = self.sock.recvfrom(1024)
                msg = {data.decode(), addr}
                print(msg)
                self.received_msg.put(msg)
            except socket.timeout:
                continue


    def quit(self):
        print(f"{self.my_ip}: Bye")
        for player in self.known_peers:
            self.sock.sendto(f"{self.my_ip}:QUIT".encode(), (player, PORT))


#peer = Peer("yo")
#listening_thread = threading.Thread(target=peer.search_for_peers)
#broadcast_thread = threading.Thread(target=peer.broadcast)
#listening_thread.start()
#broadcast_thread.start()