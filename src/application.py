import sys
from process import Process

def main(pid):
    process = Process(pid)
    try:
        while True:
            message = input("Mensaje a broadcast (o 'exit'): ")
            if message.lower() == 'exit':
                break
            process.broadcast(message)
    except KeyboardInterrupt:
        print("\nApagando proceso...")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python application.py <process_id>")
        sys.exit(1)
    main(sys.argv[1])