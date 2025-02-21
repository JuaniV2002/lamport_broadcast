# config.py
NUM_PROCESSES = 5  # Change this value to support any number of processes
BASE_PORT = 5000

# Automatically generate process configurations for p1, p2, ..., pN.
PROCESSES = {
    f'p{i+1}': {'host': 'localhost', 'port': BASE_PORT + i}
    for i in range(NUM_PROCESSES)
}

ELECTION_TIMEOUT = 5
HEARTBEAT_INTERVAL = 1