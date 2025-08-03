import sys
from Process import Process

def main(pid):
    current_process = Process(pid)
    try:
        while True:
            prompt = current_process.get_prompt()
            message = input(prompt)
            current_process.broadcast(message)
    except KeyboardInterrupt:
        print("\nShutting down process...")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Use: python application.py <process_id>")
        sys.exit(1)
    main(sys.argv[1])