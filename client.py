import socket
import threading
import time
import sys

class BroadcastClient:
    def __init__(self, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('127.0.0.1', int(port))
        self.client_socket.bind(self.server_address)
        self.role = 'follower'
        self.leader = None
        self.neighborns = []

# <--------------------------------------------------------------------------------->

    #* metodo de distribucion del mensage hacia los vecinos
    def broadcast(self, msg):
        for neighbor in self.neighborns:
            self.client_socket.sendto(msg.encode(), neighbor)

    #* proboca una eleccion para elegir el priximo leader
    def election(self):
        self.leader = None
        self.broadcast('election')

    #* pregunta cada 1s si es leader sigue conectado
    def isAlive(self):
        while True:
            heartbeat, laddr = self.client_socket.recvfrom(1024)
            if heartbeat != '❤️':
                self.election()
            time.sleep(1)

    #* señal del leader para dar a conocer que está conectado
    def heartbeat(self):
        self.broadcast('❤️')

    #* primer mensaje broadcast para saber que procesos de encuentran activos
    def greet(self):
        msg = '___'
        for i in range(5000, 5010):
            self.client_socket.sendto(msg.encode(), ('localhost', i))

# <--------------------------------------------------------------------------------->

    def listen_for_messages(self):
        while True:
            try:
                msg, addr = self.client_socket.recvfrom(1024)
                sec = msg.partition(b'---')

                if addr not in self.neighborns:
                    self.neighborns.append(addr)

                if addr != self.server_address:
                    if sec[2] != 'leader' and self.role != 'leader':
                        self.client_socket.sendto(msg.encode(), self.leader)
                    else:
                        print(f"Mensaje recibido: {sec[0].decode()}")

                if self.role == 'leader':
                    self.client_socket.sendto('❤️'.encode(), self.server_address)
                    self.client_socket.sendto(msg, addr)

            except Exception as e:
                print(f"Error: {e}")
                break

    #* metodo que inicia el proceso
    def start(self):
        self.listener = threading.Thread(target=self.listen_for_messages)
        self.listener.start()
        self.greet()

        #* si tengo vecinos detecto al leader y empiezo a escuchar el heartbeat
        if self.neighborns.__len__ != 0:
            self.heartControl = threading.Thread(target=self.isAlive)
            self.heartControl.start()

        try:
            while True:
                msg = input("Escribe un mensaje para enviar: ")
                if 'leader' in msg:
                    self.role = 'leader'
                secVal = str(time.localtime(time.time()).tm_sec)
                msg += '---' + secVal + '---' + self.role
                self.broadcast(msg)
        except KeyboardInterrupt:
            print(f"Proceso terminado")
        finally:
            self.client_socket.close()
            self.listener.join()


if __name__ == "__main__":
    client = BroadcastClient(sys.argv[1])
    client.start()