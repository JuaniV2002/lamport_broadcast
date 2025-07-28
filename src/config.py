NUM_PROCESSES = 2  # Adjust as needed
BASE_PORT = 6000

PROCESSES = {
    'p1': {'host': 'localhost', 'port': BASE_PORT},
    'p2': {'host': 'localhost', 'port': BASE_PORT + 1}
}