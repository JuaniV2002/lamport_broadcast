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

    #* Método para difundir el mensaje a todos los vecinos
    def broadcast(self, msg):
        for neighbor in self.neighbors:
            self.client_socket.sendto(msg.encode(), neighbor)

    #* Inicia la elección para determinar un nuevo líder
    def election(self):
        # Si ya hay un líder activo (heartbeat reciente), no iniciar la elección
        if self.leader is not None and (time.time() - self.last_heartbeat) < self.heartbeat_timeout:
            print("Líder activo detectado, abortando elección.")
            return

        # Si no se recibe heartbeat en el tiempo esperado,
        # se procede a iniciar la elección
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
            # Inicia el proceso de envío de heartbeats
            self.beat = threading.Thread(target=self.heartbeat)
            self.beat.start()
            print(f'El proceso {self.server_address} se ha convertido en el nuevo líder')

    # Envía o recibe heartbeats
    def heartbeat(self):
        while True:
            if self.role == 'leader':
                # Como líder, enviar heartbeat a cada vecino
                for neighbor in self.neighbors:
                    self.client_socket.sendto(b'heartbeat', neighbor)
                time.sleep(1)
            else:
                try:
                    msg, addr = self.client_socket.recvfrom(1024)
                    if msg == b'heartbeat':
                        self.last_heartbeat = time.time()
                except socket.timeout:
                    # Podrías agregar un contador de fallos aquí para disparar una elección
                    pass

    def whoIsLeader(self):
        if not self.neighbors:
            self.role = 'leader'
        else:
            # Aquí podrías agregar lógica para preguntar a los vecinos por el líder
            pass

    def isAlive(self):
        while True:
            # Lógica para verificar la conexión
            time.sleep(1)

    def greet(self):
        msg = b'___'
        for i in range(5000, 5010):
            target = ('127.0.0.1', i)
            self.client_socket.sendto(msg, target)

    def listen_for_messages(self):
        while True:
            try:
                msg, addr = self.client_socket.recvfrom(1024)
                # Lógica para manejar el mensaje recibido
            except socket.timeout:
                pass

    def sendToLeader(self, role, msg):
        if role != 'leader' and self.role != 'leader':
            # Lógica para enviar mensajes al líder
            pass
        else:
            # Elaborar mensaje especial para el líder
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