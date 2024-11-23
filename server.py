import socket
import threading

class BroadcastServer:
    def __init__(self, host='localhost', port=5000):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((host, port))
        self.clients = []
        self.role = 'follower'

    def handle_client(self):
        while True:
            msg, client_addr = self.server_socket.recvfrom(1024)
            sec = msg.partition(b'---')
            if client_addr not in self.clients:
                self.clients.append(client_addr)
                print(f"Mensaje recibido de {client_addr}: {sec[0].decode()}")
                for cli in self.clients:
                    self.broadcast(msg, ('localhost', 5001))
            else:
                for cli in self.clients:
                    print(f"Mensaje recibido de {client_addr}: {sec[0].decode()}")
                    self.broadcast(msg, ('localhost', 5001))


    def broadcast(self, msg, sender_addr):
        for client in self.clients:
            if client != sender_addr:
                self.server_socket.sendto(msg, client)

    def start(self):
        print("Servidor de Broadcast en funcionamiento...")
        while True:
            # msg, addr = self.server_socket.recvfrom(1024)
            threading.Thread(target=self.handle_client()).start()

if __name__ == "__main__":
    server = BroadcastServer()
    server.start()