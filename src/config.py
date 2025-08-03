BASE_PORT = 5000
PARTITION_SIZE = 2  # Number of processes in the system

PROCESSES = {
    'p1': {'host': 'localhost', 'port': BASE_PORT},
    'p2': {'host': 'localhost', 'port': BASE_PORT + 1},
    'p3': {'host': 'localhost', 'port': BASE_PORT + 2}
}

# To test on different computers, same local IP:

# BASE_PORT = 6000

# PROCESSES = {
#     'p1': {'host': '192.168.1.MY_IP', 'port': BASE_PORT},
#     'p2': {'host': '192.168.1.OTHER_IP', 'port': BASE_PORT}
# }