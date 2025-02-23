NUM_PROCESSES = 10  # Change this value as needed
BASE_PORT = 5000

# Determine the number of digits for zero-padding based on NUM_PROCESSES.
num_digits = len(str(NUM_PROCESSES))

# Automatically generate process configurations for p01, p02, ..., pN.
PROCESSES = {
    f'p{str(i+1).zfill(num_digits)}': {'host': 'localhost', 'port': BASE_PORT + i}
    for i in range(NUM_PROCESSES)
}

ELECTION_TIMEOUT = 5
HEARTBEAT_INTERVAL = 1