import sys
import socket
import threading
import json
from config import PROCESSES

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
        
        # Network Server Setup
        self._setup_udp_server()
        
        # Background Services
        self._start_background_threads()

    # -----------------------------
    # Initialization and Setup
    # -----------------------------
    def _validate_and_set_pid(self, pid):
        """Validate and normalize the process ID"""
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
        """Configure neighbor nodes based on partition topology"""
        # Find neighbor nodes in adjacent partitions
        self.nodes = {
            n: PROCESSES[n] 
            for n in PROCESSES 
            if n != self.pid and n in PROCESSES[self.pid]['neighbors']
        }
        
        # Initialize message tracking for each neighbor
        self.process_msgs = {}
        for p in self.nodes.keys():
            self.process_msgs[p] = (list(), 0)

    def _setup_udp_server(self):
        """Configure and bind the UDP server socket"""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))

    def _sort_neighbor_msgs(self):
        """Sort messages from neighbors based on their IDs"""
        while True:
            for node_id, (msgs, last_id) in self.process_msgs.items():
                msgs.sort(key=lambda x: int(x['id']))
            
                for msg in msgs:
                    if msg['id']-1 == last_id:
                        self.pending_messages.append(msg)
                        msgs.remove(msg)  # Remove delivered message
                        self.process_msgs[node_id] = (msgs, msg['id'])
                    else:
                        break
            self.deliver_messages()
            threading.Event().wait(0.1)  # Sleep to avoid busy waiting

    def _start_background_threads(self):
        """Start background threads for message handling"""
        threading.Thread(target=self.listen_messages, daemon=True).start()
        threading.Thread(target=self._sort_neighbor_msgs, daemon=True).start()

        self._display_neighbors()

    def _display_neighbors(self):
        """Display the immediate neighbor nodes of this process"""
        if self.nodes:
            neighbor_ids = list(self.nodes.keys())
            neighbor_str = ", ".join(neighbor_ids)
            print(f"\n[{self.pid}] Immediate neighbors: {neighbor_str}")
        else:
            print(f"\n[{self.pid}] No immediate neighbors found")

    # -----------------------------
    # Prompt & Display
    # -----------------------------
    def get_prompt(self):
        """Generate the command prompt with process ID and clock"""
        return f"[{self.pid} | Clock: {self.lamport_clock}] Enter message: "

    def print_chat(self, text):
        """Display a chat message with color formatting"""
        # Clear current line and print chat message in color, then restore prompt
        sys.stdout.write('\r\033[K')  # Clear line
        colored_text = f"\033[96m{text}\033[0m"
        print(colored_text)
        sys.stdout.write(self.get_prompt())
        sys.stdout.flush()

    # -----------------------------
    # Network Communication
    # -----------------------------
    def send_to_node(self, node, message):
        """Send a message to a specific node via UDP"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                data = json.dumps(message).encode()
                s.sendto(data, (node['host'], node['port']))
                return True
        except Exception as e:
            print(f"Error sending to {node}: {e}")
            return False

    def flood_message(self, message, exclude_node=None):
        """Flood the message to all neighbor nodes except the excluded one"""
        for node_id in self.nodes:
            if exclude_node and node_id == exclude_node:
                continue
            self.send_to_node(self.nodes[node_id], message)

    def listen_messages(self):
        """Background thread to continuously listen for incoming messages"""
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

    # -----------------------------
    # Broadcasting and Ordering
    # -----------------------------
    def broadcast(self, message_text):
        """Broadcast a message to all neighbor nodes with proper ordering"""
        # Increment clock and create a unique message ID.
        with self.lock:
            current_clock = self.lamport_clock
            self.lamport_clock += 1

        # Create the message.
        message = {
            'id': self.msg_id,
            'sender': self.pid,
            'timestamp': current_clock,
            'message': message_text,
        }
        self.msg_id += 1

        # Process the message locally first
        self.handle_message(message)
        
        # Flood the message to all neighbor nodes
        self.flood_message(message)

    def handle_message(self, data):
        """Process incoming messages with proper ordering and flooding"""
        msg_sender = data['sender']
        msg_timestamp = data['timestamp']

        with self.lock:
            self.lamport_clock = max(msg_timestamp, self.lamport_clock + 1)

        # The message has already been delivered or is waiting to be delivered
        if self.is_old_msg(data):
            return
        
        # If this message didn't originate from us, flood it to other neighbors
        self.flood_message(data, exclude_node=msg_sender)

        # Add the message to the process_msgs list for this sender to process later
        if msg_sender in self.process_msgs:
            self.process_msgs[msg_sender][0].append(data)
        else:
            self.pending_messages.append(data)
        self.deliver_messages()

    def is_old_msg(self, msg):
        """Check if the message has already been delivered or is waiting to be delivered"""
        if msg['sender'] == self.pid:
            return True
        is_delivered = (msg['id'], msg['sender']) in self.delivered
        if msg['sender'] not in self.process_msgs:
            return is_delivered
        is_waiting = msg in self.process_msgs[msg['sender']][0]
        return is_delivered or is_waiting

    def deliver_messages(self):
        """Deliver pending messages in proper timestamp order"""
        self.pending_messages.sort(key=lambda msg: (msg['timestamp'], msg['sender']))
        delivered_any = True
        while delivered_any:
            delivered_any = False
            if self.pending_messages.__len__() > 0:
                msg = self.pending_messages[0]
                if msg['id'] not in self.delivered:
                    self.print_chat(f"[{msg['sender']} | {msg['timestamp']}] {msg['message']}")
                    self.delivered.add((msg['id'], msg['sender']))
                    self.pending_messages.pop(0)
                    delivered_any = True
