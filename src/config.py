NUM_PROCESSES = 2  # Adjust as needed
BASE_PORT = 5000

# Zero-pad process IDs so that lexicographical order matches numeric order.
num_digits = len(str(NUM_PROCESSES))
PROCESSES = {
    f'p{str(i+1).zfill(num_digits)}': {'host': 'localhost', 'port': BASE_PORT + i}
    for i in range(NUM_PROCESSES)
}