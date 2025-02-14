import threading
import time
from src.BroadcastSystem import BroadcastSystem

def main():
    num_processes = 3  # Puedes ajustar el número de procesos
    system = BroadcastSystem()
    system.init_processes(num_processes)

    # Asignar a cada proceso la lista de vecinos (excluyéndose a sí mismo)
    for process in system.processes:
        process.neighbors = [p.server_address for p in system.processes if p.server_address != process.server_address]
    
    # Iniciar cada proceso en un hilo separado
    threads = []
    for process in system.processes:
        t = threading.Thread(target=process.start)
        t.daemon = True  # Para que se terminen cuando se cierre el script
        t.start()
        threads.append(t)
    
    # Dar un tiempo para que se inicien los procesos y realicen su saludo y elección de líder
    time.sleep(5)
    
    # Simular el envío de un mensaje desde uno de los procesos
    # Si el proceso no es líder, enviará el mensaje al líder
    print("\nEnviando mensaje desde el proceso 2")
    system.processes[1].sendAnyMessage("Hola desde el proceso 2")
    
    # Mantener la simulación en ejecución por un tiempo
    time.sleep(10)

if __name__ == "__main__":
    main()