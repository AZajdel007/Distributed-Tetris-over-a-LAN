import socket
import time
import threading

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
    def __init__(self, discovery_msg):
        self.my_ready_status = False
        self.discovery_msg = discovery_msg
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(("0.0.0.0", PORT))
        self.my_ip = self.get_my_ip()
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

            if msg == self.discovery_msg:
                self.sock.sendto(f"PLAYER_RESPONSE:{self.my_ip}:{self.my_ready_status}".encode(), addr)
                print(f"Wyslano: PLAYER_RESPONSE:{self.my_ip}:{self.my_ready_status} do {sender_ip}")

            elif msg.startswith("PLAYER_RESPONSE:"):
                player_ip = msg.split(":")[1]
                player_ready_status = msg.split(":")[2]
                if player_ip not in self.known_peers:
                    self.known_peers[player_ip] = player_ready_status
                print(self.known_peers)

    def broadcast(self):
        while True:
            self.sock.sendto(self.discovery_msg.encode(), (BROADCAST_IP, PORT))


            time.sleep(2)




peer = Peer("yo")
thread1 = threading.Thread(target=peer.search_for_peers)
thread2 = threading.Thread(target=peer.broadcast)
thread1.start()
thread2.start()