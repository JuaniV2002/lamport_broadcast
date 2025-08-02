import sys
import socket
import threading
import json
from config import PROCESSES, PARTITION_SIZE

class Process:
    def __init__(self, pid):
        # Process ID Validation & Setup
        self.original_pid = pid
        self._validate_and_set_pid(pid)
        
        # Basic Process Configuration
        self.host = PROCESSES[self.pid]['host']
        self.port = PROCESSES[self.pid]['port']
        self.msg_id = 1
        
        # Network Topology Setup
        self._setup_neighbor_nodes()
        
        # Synchronization & Timing
        self.lamport_clock = 0
        self.lock = threading.Lock()
        
        # Message Ordering & Delivery
        self.pending_messages = []
        self.delivered = set()  # track delivered message ids
        self.seen_messages = set()
        
        # Network Server Setup
        self._setup_udp_server()
        
        # Background Services
        self._start_background_threads()

    def _validate_and_set_pid(self, pid):
        # Validate and normalize the process ID
        if pid not in PROCESSES:
            if pid.startswith('p'):
                num = pid[1:]
                # Search for the corresponding key in PROCESSES
                for key in PROCESSES:
                    if key.startswith('p') and key[1:].lstrip('0') == num:
                        pid = key
                        break
        
        # If still not found, raise an error
        if pid not in PROCESSES:
            print(f"Error: Process '{self.original_pid}' not found. Valid IDs: {list(PROCESSES.keys())}")
            sys.exit(1)
        
        self.pid = pid

    def _setup_neighbor_nodes(self):
        # Configure neighbor nodes based on partition topology
        previous_mod = (int(self.pid[1:]) - 1) % PARTITION_SIZE
        next_mod = (int(self.pid[1:]) + 1) % PARTITION_SIZE
        
        # Find neighbor nodes in adjacent partitions
        self.nodes = {
            n: PROCESSES[n] 
            for n in PROCESSES 
            if n != self.pid and (
                int(n[1:]) % PARTITION_SIZE == previous_mod or 
                int(n[1:]) % PARTITION_SIZE == next_mod
            )
        }
        
        # Initialize message tracking for each neighbor
        self.process_msgs = {}
        for p in self.nodes.keys():
            self.process_msgs[p] = (list(), 0)

    def _setup_udp_server(self):
        # Configure and bind the UDP server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))

    def _start_background_threads(self):
        # Start background threads for message handling
        threading.Thread(target=self.listen_messages, daemon=True).start()

    # -----------------------------
    # Prompt & Print Helpers
    # -----------------------------
    def get_prompt(self):
        return f"[{self.pid} | Clock: {self.lamport_clock}] Enter message: "

    def print_chat(self, text):
        # Clear current line and print chat message in color, then restore prompt
        sys.stdout.write('\r\033[K')  # Clear line
        colored_text = f"\033[96m{text}\033[0m"
        print(colored_text)
        sys.stdout.write(self.get_prompt())
        sys.stdout.flush()

    # -----------------------------
    # Communication Helpers
    # -----------------------------
    def send_to_node(self, node, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                data = json.dumps(message).encode()
                s.sendto(data, (node['host'], node['port']))
                return True
        except Exception as e:
            print(f"Error sending to {node}: {e}")
            return False

    # -----------------------------
    # Flooding Implementation
    # -----------------------------
    def flood_message(self, message, exclude_node=None):
        # Floods the message to all neighbor nodes except the one specified in exclude_node
        for node_id in self.nodes:
            if exclude_node and node_id == exclude_node:
                continue
            self.send_to_node(self.nodes[node_id], message)

    # -----------------------------
    # Broadcasting
    # -----------------------------
    def broadcast(self, message_text):
        # Step 1: Increment clock and create a unique message ID.
        with self.lock:
            current_clock = self.lamport_clock
            self.lamport_clock += 1

        # Create the message.
        message = {
            'id': self.msg_id,
            'sender': self.pid,
            'timestamp': current_clock,
            'message': message_text,
            'originator': self.pid  # Track the original sender for flooding
        }
        self.msg_id += 1

        # Mark this message as seen to avoid processing it again
        message_key = (message['sender'], message['id'])
        self.seen_messages.add(message_key)

        # Process the message locally first
        self.handle_message(message)
        
        # Flood the message to all neighbor nodes
        self.flood_message(message)

    def deliver_messages(self):
        # Sort pending messages by final_timestamp and then by sender (as a tie-breaker).
        self.pending_messages.sort(key=lambda msg: (msg['timestamp'], msg['sender']))
        delivered_any = True
        while delivered_any:
            delivered_any = False
            if self.pending_messages:
                msg = self.pending_messages[0]
                if msg['id'] not in self.delivered:
                    self.print_chat(f"[{msg['sender']} | {msg['timestamp']}] {msg['message']}")
                    self.delivered.add((msg['id'], msg['sender']))
                    self.pending_messages.pop(0)
                    delivered_any = True

    # -----------------------------
    # Message Handling
    # -----------------------------
    def max_id(self, sender):
        id = 0
        for msg in self.process_msgs[sender][0]:
            id = max(id, int(msg[0]))
        return id

    def handle_message(self, data):
        msg_id = data['id']
        msg_sender = data['sender']
        msg_timestamp = data['timestamp']
        msg = data['message']
        originator = data.get('originator', msg_sender)

        message_key = (msg_sender, msg_id)
        if message_key in self.seen_messages:
            return  # Already processed this message
        
        self.seen_messages.add(message_key)

        with self.lock:
            self.lamport_clock = max(msg_timestamp, self.lamport_clock + 1)

        # If this message didn't originate from us, flood it to other neighbors
        if originator != self.pid:
            # Find which neighbor sent us this message to avoid sending it back
            # sender_node_id = None
            for node_id, node_info in PROCESSES.items():
                if node_info['host'] == self.host and node_info['port'] == self.port:
                    continue  # Skip ourselves
            
            self.flood_message(data)

        if ((msg_id , msg_sender) in self.delivered):
            return # The message has already been delivered

        # Only process messages from our direct neighbors for ordering
        if msg_sender in self.process_msgs:
            # Check if the message is out of order
            if int(msg_id)-1 != int(self.process_msgs[msg_sender][1]) and int(msg_id) > int(self.process_msgs[msg_sender][1]):
                self.process_msgs[msg_sender][0].append((msg_id, msg))

            # If the message is in order, deliver it
            elif int(msg_id)-1 == int(self.process_msgs[msg_sender][1]) and self.max_id(msg_sender) <= int(msg_id)-1:
                lista = self.process_msgs[msg_sender][0]
                lista.append((msg_id, msg))
                self.process_msgs[msg_sender] = (lista, msg_id)
                self.pending_messages.append(data)
        else:
            # For messages from non-direct neighbors (received via flooding), just add to pending
            self.pending_messages.append(data)

        self.deliver_messages()

    # -----------------------------
    # Background Threads
    # -----------------------------
    def listen_messages(self):
        while True:
            try:
                data, _ = self.server.recvfrom(1024)
                try:
                    message = json.loads(data.decode())
                    self.handle_message(message)
                except Exception as e:
                    print("Error processing message:", e)
            except Exception as e:
                print(f"Error receiving message: {e}")