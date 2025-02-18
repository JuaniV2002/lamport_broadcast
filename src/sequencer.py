import socket
import threading
import json
import queue

from config import SEQUENCER

class Sequencer:
    def __init__(self):
        self.sequence_number = 0
        self.connected_processes = {}  # {id: socket}
        self.lock = threading.Lock()
        self.broadcast_queue = queue.Queue()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((SEQUENCER['host'], SEQUENCER['port']))
        self.server_socket.listen(5)

    def start(self):
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.daemon = True
        accept_thread.start()

        worker_thread = threading.Thread(target=self.process_broadcasts)
        worker_thread.daemon = True
        worker_thread.start()

        accept_thread.join()
        worker_thread.join()

    def accept_connections(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            handler_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            handler_thread.daemon = True
            handler_thread.start()

    def handle_client(self, client_socket):
        buffer = ''
        try:
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    msg = json.loads(line)
                    if msg['type'] == 'register':
                        pid = msg['id']
                        with self.lock:
                            self.connected_processes[pid] = client_socket
                    elif msg['type'] == 'broadcast':
                        sender_id = pid
                        self.broadcast_queue.put((sender_id, msg['message']))
        except Exception as e:
            print(f"Error: {e}")
        finally:
            with self.lock:
                for pid, sock in list(self.connected_processes.items()):
                    if sock == client_socket:
                        del self.connected_processes[pid]
            client_socket.close()

    def process_broadcasts(self):
        while True:
            sender_id, message = self.broadcast_queue.get()
            with self.lock:
                self.sequence_number += 1
                seq = self.sequence_number
                ordered_msg = json.dumps({
                    'type': 'ordered',
                    'seq': seq,
                    'sender': sender_id,
                    'message': message
                }) + '\n'
                for pid, sock in list(self.connected_processes.items()):
                    try:
                        sock.send(ordered_msg.encode())
                    except:
                        del self.connected_processes[pid]

if __name__ == "__main__":
    sequencer = Sequencer()
    sequencer.start()