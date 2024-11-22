
from src import Process

# Representa una abstracción del sistema
class BroadcastSystem:
    def __init__(self):
        self.processes = []

    def init_processes(self, num_processes):
        for i in range(num_processes):
            self.processes.append(Process(i))

    def collect_confirmations(self, msg):
        confirmations = []
        for process in self.processes:
            confirmation = process.confirm_receipt(msg)
            confirmations.append(confirmation)
        return confirmations

    def handle_failures(self):
        failed_processes = []
        for process in self.processes:
            if not process.is_active():
                failed_processes.append(process)
        return failed_processes