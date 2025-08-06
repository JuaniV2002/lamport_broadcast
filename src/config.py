BASE_PORT = 5000

PROCESSES = {
    'p1': {'host': 'localhost', 'port': BASE_PORT, 'neighbors': ['p2']},
    'p2': {'host': 'localhost', 'port': BASE_PORT + 1, 'neighbors': ['p1', 'p3']},
    'p3': {'host': 'localhost', 'port': BASE_PORT + 2, 'neighbors': ['p2']},
}