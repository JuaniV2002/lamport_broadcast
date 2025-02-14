import socket

# Representa cada proceso del sistema
class Process:
    def __init__(self, id, host, port):
        self.id = id
        self.host = host
        self.port = port
        self.server_address = (host, port)
        self.state = 'correct'
        self.message_queue = []
        
        # Crea y vincula el socket UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.socket.bind(self.server_address)
            print(f"Proceso {id} ligado a {self.server_address}")
        except Exception as e:
            print(f"Error al vincular el proceso {id} en {self.server_address}: {e}")

    def send_message(self, msg, processes):
        for process in processes:
            self.socket.sendto(msg.encode(), process.server_address)

    def receive_message(self, msg):
        self.message_queue.append(msg)

    def broadcast(self, msg, processes):
        self.send_message(msg, processes)
        # Aquí podrías agregar lógica para esperar confirmaciones

    def deliver_messages(self):
        # Lógica para entregar mensajes en el orden correcto
        pass

    # Ejemplo de método para confirmar la recepción de un mensaje
    def confirm_receipt(self, msg):
        # Aquí podrías implementar la confirmación
        return f"Proceso {self.id} confirmó el mensaje: {msg}"

    # Ejemplo de método para determinar si el proceso está activo
    def is_active(self):
        # Una implementación simple que siempre retorna True
        return True