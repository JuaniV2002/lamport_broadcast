import socket
import threading
import time
import sys

class BroadcasterProcess:
    def __init__(self, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('127.0.0.1', int(port))
        self.client_socket.bind(self.server_address)
        self.client_socket.settimeout(2)
        self.role = 'follower'
        self.leader = None
        self.neighbors = []

# <--------------------------------------------------------------------------------->

    #* metodo de distribucion del mensage hacia los vecinos
    def broadcast(self, msg):
        for neighbor in self.neighbors:
            self.client_socket.sendto(msg.encode(), neighbor)

    #* proboca una eleccion para elegir el priximo leader
    def election(self):
        self.leader = None
        self.role = 'candidate'
        msg = 'election'
        cantVotes = 0
        for neighbor in self.neighbors:
            self.client_socket.sendto(msg.encode(), neighbor)
            msg, addr = self.client_socket.recvfrom(1024)
            if msg != 'accept':
                cantVotes += 1
            else:
                break
        if not self.neighbors or cantVotes == len(self.neighbors )-1:
            self.role = 'leader'
            self.leader = self
            print(f'El proceso {self.server_address} se ha convertido en el nuevo líder')

    def whoIsLeader(self):
        if not self.neighbors:
            self.role = 'leader'
            self.leader = self
        else:
            for neighbor in self.neighbors:
                self.client_socket.sendto('whoIsLeader'.encode(), neighbor)
                msg, addr = self.client_socket.recvfrom(1024)

                if 'leader' in msg:
                    self.leader = addr
                    break
        

    #* pregunta cada 1s si es leader sigue conectado
    def isAlive(self):
        while True:
            try:
                heartbeat, laddr = self.client_socket.recvfrom(1024)
                if heartbeat != '❤️':
                    self.election()
            except TimeoutError:
                self.election()
            time.sleep(1)

    #* señal del leader para dar a conocer que está conectado
    def heartbeat(self):
        while True:
            self.broadcast('❤️')
            time.sleep(1)

    #* primer mensaje broadcast para saber que procesos de encuentran activos
    def greet(self):
        msg = b'___'
        for i in range(5000, 5010):
            dest = ('127.0.0.1', i)
            self.client_socket.sendto(msg, dest)
            try:
                msg, addr = self.client_socket.recvfrom(1024)
            except TimeoutError:
                print('time out')
            except Exception as e:
                print(f'Error en el proceso {self.server_address}: {e}')
            if msg == '___' and addr == dest and dest not in self.neighbors:
                self.neighbors.append(addr)


# <--------------------------------------------------------------------------------->

    def listen_for_messages(self):
        imPresent = False
        while True:
            try:
                msg, addr = self.client_socket.recvfrom(1024)
                sec = msg.partition(b'---')

                if msg == '___' and addr not in self.neighbors:
                    self.neighbors.append(addr)
                    self.client_socket.sendto('___', addr)
                    continue

                if sec[0] == b'election' and addr[1] > self.server_address[1]:
                    self.leader = addr
                    self.role = 'follower'
                    self.client_socket.sendto('accept', addr)
                    continue

                if sec[0] == b'election' and addr[1] <= self.server_address[1]:
                    self.leader = addr
                    self.election()
                    continue

                if addr != self.server_address:
                    self.sendToLeader(sec[2], sec[0])
                    continue

                if self.role == 'leader' and not imPresent:
                    imPresent = True
                    self.beat = threading.Thread(target=self.heartbeat)
                    self.beat.start()
                    # self.client_socket.sendto('❤️'.encode(), self.server_address)
                    # self.client_socket.sendto(msg, addr)

            except Exception as e:
                print(f"Error: {e}")
                break

    def sendToLeader(self, role, msg):
        if role != 'leader' and self.role != 'leader':
            if self.leader != None:
                self.client_socket.sendto(msg.encode(), self.leader)
            else:
                self.election()
        else:
            print(f"Mensaje recibido: {msg.decode()}")


    #* metodo que inicia el proceso
    def start(self):
        self.listener = threading.Thread(target=self.listen_for_messages)
        self.listener.start()

        self.greet()
        self.whoIsLeader()

        #* si tengo vecinos detecto al leader y empiezo a escuchar el heartbeat
        if self.neighbors and self.leader != None:
            self.heartControl = threading.Thread(target=self.isAlive)
            self.heartControl.start()

        if self.leader == None:
            self.election()            

        try:
            while True:
                msg = input("Escribe un mensaje para enviar: ")
                self.sendAnyMessage(msg)
        except KeyboardInterrupt:
            print(f"Proceso terminado")
        finally:
            self.client_socket.close()
            self.listener.join()

    def sendAnyMessage(self, msg):
        # if 'leader' in msg:
        #     self.role = 'leader'
        secVal = str(time.localtime(time.time()).tm_sec)
        msg += '---' + secVal + '---' + self.role
        self.broadcast(msg)



if __name__ == "__main__":
    client = BroadcasterProcess(sys.argv[1])
    client.start()