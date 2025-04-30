import sys
import socket
import threading
import json
import time
import random
from config import PROCESSES, NUM_PROCESSES

class Process:
    def __init__(self, pid):
        # Adaptar el pid para que funcione con o sin padding de ceros
        self.original_pid = pid
        # Si pid no está en PROCESSES, intentamos encontrar la clave correspondiente
        if pid not in PROCESSES:
            # Extraer el número de pid (quita la 'p' del inicio)
            if pid.startswith('p'):
                num = pid[1:]
                # Buscar la clave en PROCESSES que coincida con el número
                for key in PROCESSES:
                    if key.startswith('p') and key[1:].lstrip('0') == num:
                        pid = key
                        break
        
        # Si aún no encontramos el pid, mostramos un error claro
        if pid not in PROCESSES:
            print(f"Error: Proceso '{self.original_pid}' no encontrado. IDs válidos: {list(PROCESSES.keys())}")
            sys.exit(1)
            
        self.pid = pid
        self.host = PROCESSES[pid]['host']
        self.port = PROCESSES[pid]['port']
        self.nodes = {n: PROCESSES[n] for n in PROCESSES if n != pid}
        
        # Initialize Lamport clock
        self.lamport_clock = 0
        self.lock = threading.Lock()
        
        # Data structures for total order broadcast
        # For each message id, store the list of proposals received.
        self.proposals = {}   # message_id -> list of proposal timestamps
        # Hold-back queue for final messages to be delivered
        self.pending_messages = []  # each message is a dict with keys: id, final_timestamp, sender, message
        self.delivered = set()      # track delivered message ids
        
        # Configure server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        
        # Start a thread to listen for incoming connections.
        threading.Thread(target=self.listen_clients, daemon=True).start()

    # -----------------------------
    # Prompt & Print Helpers
    # -----------------------------
    def get_prompt(self):
        return f"[{self.pid} | Clock: {self.lamport_clock}] Ingrese mensaje: "

    def async_print(self, msg):
        prompt = self.get_prompt()
        sys.stdout.write('\r')
        sys.stdout.write(' ' * 80)
        sys.stdout.write('\r')
        print(msg)
        sys.stdout.write(prompt)
        sys.stdout.flush()

    def print_chat(self, text):
        colored_text = f"\033[96m{text}\033[0m"  # Bright cyan for chat messages
        self.async_print(colored_text)

    # -----------------------------
    # Communication Helpers
    # -----------------------------
    def send_to_node(self, node, message):
        try:
            with socket.create_connection((node['host'], node['port']), timeout=1) as s:
                s.send(json.dumps(message).encode())
                return True
        except:
            return False

    def broadcast_to_all(self, message):
        # Send the message to all nodes, including self.
        self.handle_message(message)
        for node_id in self.nodes:
            self.send_to_node(self.nodes[node_id], message)

    # -----------------------------
    # Total Order Broadcast (ISIS Algorithm)
    # -----------------------------
    def broadcast(self, message_text):
        # Step 1: Increment clock and create a unique message ID.
        with self.lock:
            self.lamport_clock += 1
            current_clock = self.lamport_clock
        message_id = f"{self.pid}_{current_clock}_{random.randint(0,10000)}"
        # Initialize proposals for this message.
        self.proposals[message_id] = []
        # Create a proposal request message.
        proposal_request = {
            'type': 'proposal_request',
            'id': message_id,
            'sender': self.pid,
            'tentative': current_clock,
            'message': message_text
        }
        # Broadcast the proposal request to all processes.
        self.broadcast_to_all(proposal_request)
        # Spawn a thread to wait for proposals and then send the final message.
        threading.Thread(target=self.collect_and_send_final, args=(message_id, proposal_request), daemon=True).start()

    def collect_and_send_final(self, message_id, proposal_request):
        # Wait until proposals from all processes have been collected.
        while len(self.proposals[message_id]) < len(PROCESSES):
            time.sleep(0.05)
        # Final timestamp is the maximum of all proposals.
        final_timestamp = max(self.proposals[message_id])
        with self.lock:
            self.lamport_clock = max(self.lamport_clock, final_timestamp) + 1
        # Create the final message.
        final_message = {
            'type': 'final',
            'id': message_id,
            'final_timestamp': final_timestamp,
            'sender': proposal_request['sender'],
            'message': proposal_request['message']
        }
        # Broadcast the final message to all processes.
        self.broadcast_to_all(final_message)

    def deliver_messages(self):
        # Sort pending messages by final_timestamp and then by sender (as a tie-breaker).
        self.pending_messages.sort(key=lambda msg: (msg['final_timestamp'], msg['sender']))
        delivered_any = True
        while delivered_any:
            delivered_any = False
            if self.pending_messages:
                msg = self.pending_messages[0]
                if msg['id'] not in self.delivered:
                    self.print_chat(f"[{msg['sender']} | {msg['final_timestamp']}] {msg['message']}")
                    self.delivered.add(msg['id'])
                    self.pending_messages.pop(0)
                    delivered_any = True

    # -----------------------------
    # Message Handling
    # -----------------------------
    def handle_message(self, data):
        msg_type = data.get('type')
        if msg_type == 'proposal_request':
            # When receiving a proposal request, update local clock.
            tentative = data.get('tentative', 0)
            with self.lock:
                self.lamport_clock = max(self.lamport_clock, tentative) + 1
                proposal = self.lamport_clock
            # Send back a proposal reply.
            reply = {
                'type': 'proposal_reply',
                'id': data['id'],
                'proposal': proposal,
                'sender': self.pid
            }
            if data['sender'] == self.pid:
                # If the request originated here, handle directly.
                self.handle_message(reply)
            else:
                self.send_to_node(PROCESSES[data['sender']], reply)

        elif msg_type == 'proposal_reply':
            # Only the originator of the message collects proposals.
            message_id = data['id']
            if message_id in self.proposals:
                self.proposals[message_id].append(data['proposal'])
                with self.lock:
                    self.lamport_clock = max(self.lamport_clock, data['proposal']) + 1

        elif msg_type == 'final':
            # On receiving the final message, update clock and add to pending messages.
            final_timestamp = data.get('final_timestamp', 0)
            with self.lock:
                self.lamport_clock = max(self.lamport_clock, final_timestamp) + 1
            self.pending_messages.append(data)
            self.deliver_messages()

    # -----------------------------
    # Background Threads
    # -----------------------------
    def listen_clients(self):
        while True:
            client, addr = self.server.accept()
            threading.Thread(target=self.client_handler, args=(client,), daemon=True).start()

    def client_handler(self, client):
        try:
            while True:
                data = client.recv(1024)
                if not data:
                    break
                try:
                    message = json.loads(data.decode())
                    self.handle_message(message)
                except Exception as e:
                    print("Error processing message:", e)
        except Exception as e:
            pass
        finally:
            client.close()