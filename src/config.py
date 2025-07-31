BASE_PORT = 6000

PROCESSES = {
    'p1': {'host': 'localhost', 'port': BASE_PORT},
    'p2': {'host': 'localhost', 'port': BASE_PORT + 1}
}

# To test on different computers, same local IP:

# BASE_PORT = 6000

# PROCESSES = {
#     'p1': {'host': '192.168.1.MY_IP', 'port': BASE_PORT},
#     'p2': {'host': '192.168.1.OTHER_IP', 'port': BASE_PORT}
# }