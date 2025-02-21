import sys
import socket
import threading
import json
import time
import random
from config import PROCESSES, ELECTION_TIMEOUT, HEARTBEAT_INTERVAL

class Process:
    def __init__(self, pid):
        self.pid = pid
        self.host = PROCESSES[pid]['host']
        self.port = PROCESSES[pid]['port']
        self.leader = None
        self.sequence_number = 0
        self.nodes = {n: PROCESSES[n] for n in PROCESSES if n != pid}
        self.is_leader = False
        self.election_in_progress = False
        self.last_heartbeat = time.time()
        self.lock = threading.Lock()
        self.pending_messages = []
        
        # Configurar servidor
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        
        # Iniciar hilos
        threading.Thread(target=self.listen_clients, daemon=True).start()
        threading.Thread(target=self.heartbeat_checker, daemon=True).start()
        threading.Thread(target=self.discover_leader, daemon=True).start()

    # ----------------------------------------
    # Prompt & Print Helpers
    # ----------------------------------------
    def get_prompt(self):
        current_leader = self.leader if self.leader else "Desconocido"
        return f"[{self.pid} | Líder: {current_leader}] Ingrese mensaje: "

    def async_print(self, msg):
        """
        Clears the current input line, prints an asynchronous message, 
        and reprints the prompt so that the user can continue typing.
        """
        prompt = self.get_prompt()
        # Move cursor to start of line:
        sys.stdout.write('\r')
        # Overwrite with spaces (80 is arbitrary; adjust as needed):
        sys.stdout.write(' ' * 80)
        # Move cursor back again:
        sys.stdout.write('\r')

        print(msg)  # Print the asynchronous message
        sys.stdout.write(prompt)  # Re-print the prompt
        sys.stdout.flush()

    def print_chat(self, text):
        """
        Prints a 'chat feed' message in a different style/color 
        so it looks distinct from the user prompt.
        """
        # Example: ANSI escape code \033[96m for bright cyan text.
        # Ends with \033[0m to reset the color.
        colored_text = f"\033[96m{text}\033[0m"
        self.async_print(colored_text)

    # ----------------------------------------
    # Communication & Broadcast
    # ----------------------------------------
    def send_to_node(self, node, message):
        try:
            with socket.create_connection((node['host'], node['port']), timeout=1) as s:
                s.send(json.dumps(message).encode())
                return True
        except:
            return False

    def broadcast_ordered(self, message):
        # Let *this* process handle the message as well
        self.handle_message(message)
        # Then send to all other nodes
        for node_id in self.nodes:
            self.send_to_node(self.nodes[node_id], message)

    # ----------------------------------------
    # Leader Election Logic
    # ----------------------------------------
    def discover_leader(self):
        time.sleep(1)  # Esperar inicialización de otros nodos
        for node_id in sorted(self.nodes, reverse=True):
            if self.send_to_node(self.nodes[node_id], {'type': 'leader_inquiry'}):
                return
        self.start_election()

    def start_election(self):
        if self.election_in_progress:
            return
        self.election_in_progress = True

        self.print_chat(f"Iniciando elección desde {self.pid}...")
        higher_nodes = [n for n in self.nodes if n > self.pid]
        if not higher_nodes:
            self.become_leader()
            return

        election_ack = False
        for node_id in higher_nodes:
            if self.send_to_node(self.nodes[node_id], {'type': 'election'}):
                election_ack = True
                break

        if not election_ack:
            self.become_leader()

        self.election_in_progress = False

    def become_leader(self):
        self.print_chat(f"*** {self.pid} ES AHORA EL LÍDER ***")
        self.is_leader = True
        self.leader = self.pid
        self.announce_leadership()
        self.process_pending_messages()

    def announce_leadership(self):
        for node_id in self.nodes:
            self.send_to_node(self.nodes[node_id], {
                'type': 'new_leader',
                'leader': self.pid
            })

    # ----------------------------------------
    # Message Handling
    # ----------------------------------------
    def handle_message(self, data):
        if data['type'] == 'heartbeat':
            self.last_heartbeat = time.time()
            if data['leader'] != self.leader:
                self.leader = data['leader']
                self.print_chat(f"Líder actualizado: {self.leader}")

        elif data['type'] == 'election':
            # Se espera que el mensaje 'sender' esté incluido en la data para responder
            sender_id = data.get('sender', '')
            if sender_id in self.nodes:
                self.send_to_node(self.nodes[sender_id], {'type': 'election_ack'})
            self.start_election()

        elif data['type'] == 'new_leader':
            self.leader = data['leader']
            self.print_chat(f"Nuevo líder asignado: {self.leader}")
            if self.is_leader:
                self.is_leader = False

        elif data['type'] == 'broadcast':
            if self.is_leader:
                with self.lock:
                    self.sequence_number += 1
                    ordered_msg = {
                        'type': 'ordered',
                        'seq': self.sequence_number,
                        'message': data['message']
                    }
                    self.broadcast_ordered(ordered_msg)
            else:
                self.pending_messages.append(data)

        elif data['type'] == 'ordered':
            # This is an actual chat message from a leader
            current_leader = self.leader if self.leader else "Desconocido"
            self.print_chat(f"[{self.pid} -> Líder: {current_leader}] {data['message']}")

    # ----------------------------------------
    # Background Threads
    # ----------------------------------------
    def heartbeat_checker(self):
        while True:
            if self.is_leader:
                self.broadcast_ordered({'type': 'heartbeat', 'leader': self.pid})
                time.sleep(HEARTBEAT_INTERVAL)
            else:
                if time.time() - self.last_heartbeat > ELECTION_TIMEOUT:
                    self.print_chat("¡Atención! Líder no responde. Iniciando elección...")
                    self.start_election()
                time.sleep(1)

    def listen_clients(self):
        while True:
            client, addr = self.server.accept()
            threading.Thread(target=self.client_handler, args=(client,), daemon=True).start()

    def client_handler(self, client):
        try:
            while True:
                data = json.loads(client.recv(1024).decode())
                self.handle_message(data)
        except:
            client.close()

    def process_pending_messages(self):
        while self.pending_messages:
            msg = self.pending_messages.pop(0)
            self.handle_message(msg)

    # ----------------------------------------
    # Public API
    # ----------------------------------------
    def broadcast(self, message):
        """
        Called by application.py whenever the user types a message.
        """
        if not message:
            return  # Ignore empty messages
        if self.is_leader:
            with self.lock:
                self.sequence_number += 1
                self.broadcast_ordered({
                    'type': 'ordered',
                    'seq': self.sequence_number,
                    'message': message
                })
        else:
            if self.leader:
                self.send_to_node(PROCESSES[self.leader], {
                    'type': 'broadcast',
                    'message': message
                })
            else:
                self.print_chat("No hay líder disponible. Mensaje en cola.")
                self.pending_messages.append({
                    'type': 'broadcast',
                    'message': message
                })