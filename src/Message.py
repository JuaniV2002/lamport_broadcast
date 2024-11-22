

import time

# Representa un mensaje que se va a enviar a través del sistema
class Message:
    def __init__(self, content, sender_id):
        self.content = content
        self.timestamp = time.time()
        self.sender_id = sender_id