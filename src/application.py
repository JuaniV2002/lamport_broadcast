import sys
from process import Process

def main(pid):
    process = Process(pid)
    while True:
        message = input("Broadcast message (or 'exit'): ")
        if message.lower() == 'exit':
            break
        process.broadcast(message)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python application.py <process_id>")
        sys.exit(1)
    main(sys.argv[1])