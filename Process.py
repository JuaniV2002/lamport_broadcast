import socket
import threading
import time
import sys

class BroadcasterProcess:
    def __init__(self, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('127.0.0.1', int(port))
        self.client_socket.bind(self.server_address)
        self.client_socket.settimeout(1)
        self.role = 'follower'
        self.leader = None
        self.neighbors = []
        self.last_heartbeat = 0  # Última vez que se recibió heartbeat
        self.heartbeat_timeout = 5  # umbral (segundos) para considerar inactivo al líder

    # Método para difundir el mensaje a todos los vecinos
    def broadcast(self, msg):
        for neighbor in self.neighbors:
            self.client_socket.sendto(msg.encode(), neighbor)

    # Inicia la elección para determinar un nuevo líder
    def election(self):
        if self.leader is not None and (time.time() - self.last_heartbeat) < self.heartbeat_timeout:
            print("Líder activo detectado, abortando elección.")
            return

        self.leader = None
        self.role = 'candidate'
        msg = b'election'
        cantVotes = 0

        for neighbor in self.neighbors:
            self.client_socket.sendto(msg, neighbor)
            try:
                reply, addr = self.client_socket.recvfrom(1024)
                if reply == b'accept':
                    cantVotes += 1
                else:
                    break
            except socket.timeout:
                pass

        print('election')
        if not self.neighbors or cantVotes == len(self.neighbors) - 1:
            self.role = 'leader'
            self.leader = self.server_address
            self.beat = threading.Thread(target=self.heartbeat)
            self.beat.start()
            print(f'El proceso {self.server_address} se ha convertido en el nuevo líder')

    # Solo envía heartbeats si es líder
    def heartbeat(self):
        while True:
            if self.role == 'leader':
                for neighbor in self.neighbors:
                    self.client_socket.sendto(b'heartbeat', neighbor)
                time.sleep(1)
            else:
                time.sleep(1)

    # Escucha todos los mensajes entrantes (incluyendo heartbeats)
    def listen_for_messages(self):
        while True:
            try:
                msg, addr = self.client_socket.recvfrom(1024)
                if msg == b'heartbeat':
                    self.last_heartbeat = time.time()
                # Aquí puedes agregar el manejo de otros mensajes (election, greetings, etc.)
            except socket.timeout:
                pass

    def whoIsLeader(self):
        if not self.neighbors:
            self.role = 'leader'
        else:
            pass

    def isAlive(self):
        while True:
            time.sleep(1)

    def greet(self):
        msg = b'___'
        for i in range(5000, 5010):
            target = ('127.0.0.1', i)
            self.client_socket.sendto(msg, target)

    def sendToLeader(self, role, msg):
        if role != 'leader' and self.role != 'leader':
            pass
        else:
            pass

    def start(self):
        self.listener = threading.Thread(target=self.listen_for_messages)
        self.listener.start()

        self.greet()
        self.whoIsLeader()

        if self.leader is None:
            try:
                self.election()
            except KeyboardInterrupt:
                pass
            finally:
                self.client_socket.close()

    def sendAnyMessage(self, msg):
        secVal = str(time.localtime(time.time()).tm_sec)
        msg += '---' + secVal + '---' + self.role
        self.broadcast(msg)


if __name__ == "__main__":
    client = BroadcasterProcess(sys.argv[1])
    client.start()