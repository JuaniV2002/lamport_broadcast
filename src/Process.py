import socket
import threading
import json

from config import SEQUENCER

class Process:
    def __init__(self, pid):
        self.pid = pid
        self.sequencer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sequencer_socket.connect((SEQUENCER['host'], SEQUENCER['port']))
        self.register()
        self.next_seq = 1
        self.listener_thread = threading.Thread(target=self.listen_sequencer)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def register(self):
        msg = json.dumps({'type': 'register', 'id': self.pid}) + '\n'
        self.sequencer_socket.send(msg.encode())

    def listen_sequencer(self):
        buffer = ''
        while True:
            data = self.sequencer_socket.recv(1024).decode()
            if not data:
                break
            buffer += data
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                msg = json.loads(line)
                if msg['type'] == 'ordered':
                    self.deliver(msg['seq'], msg['sender'], msg['message'])

    def deliver(self, seq, sender, message):
        if seq == self.next_seq:
            print(f"[{self.pid}] Deliver #{seq}: {message} (from {sender})")
            self.next_seq += 1
        else:
            print(f"Error: Expected seq {self.next_seq}, got {seq}")

    def broadcast(self, message):
        msg = json.dumps({'type': 'broadcast', 'message': message}) + '\n'
        self.sequencer_socket.send(msg.encode())