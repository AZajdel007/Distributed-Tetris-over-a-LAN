import socket
import time
import threading
import ipaddress


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


    def search_for_peers(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
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
        while True:
            self.sock.sendto(self.discovery_msg.encode(), (self.my_broadcast, PORT))


            time.sleep(2)

test = False
print(test)
test = test + 1
print(test)
test = test + 1
print(test)

peer = Peer("yo")
thread1 = threading.Thread(target=peer.search_for_peers)
thread2 = threading.Thread(target=peer.broadcast)
thread1.start()
thread2.start()
time.sleep(5)
peer.change_ready_status()