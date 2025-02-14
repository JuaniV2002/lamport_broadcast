from src import Process

# Representa una abstracción del sistema
class BroadcastSystem:
    def __init__(self):
        self.processes = []

    def init_processes(self, num_processes):
        # Ejemplo: crea procesos usando IP de red pública o alguna IP de la red virtual
        # Aquí se asigna el puerto automáticamente, por ejemplo, 5000 + id
        # Puedes cambiar "192.168.1.100" por la IP deseada de cada nodo
        default_host = "192.168.1.100"
        for i in range(num_processes):
            port = 5000 + i
            process = Process(i, default_host, port)
            self.processes.append(process)

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