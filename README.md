# Distributed Message Broadcast with Lamport Clocks

A distributed system implementation demonstrating message flooding and total ordering using Lamport logical clocks across multiple processes in a network topology.

## Features

- **Lamport Logical Clocks** - Maintains causality and timestamps across distributed processes
- **Message Flooding** - Messages propagate through neighbor connections to reach all processes  
- **Total Message Ordering** - Messages delivered in consistent timestamp order across all processes
- **Network Topology** - Configurable neighbor-based network structure
- **Real-time Chat** - Interactive console interface for message broadcasting

## Requirements

- Python 3.7+
- Standard library only (socket, threading, json)

## Project Structure

```
project2/src/
├── config.py      # Network topology configuration
├── Process.py     # Main process implementation  
├── app.py         # Process launcher
└── Launcher.sh    # Multi-terminal startup script
```

## Configuration

Edit `config.py` to define network topology:

```python
PROCESSES = {
    'p1': {'host': 'localhost', 'port': 5000, 'neighbors': ['p2']},
    'p2': {'host': 'localhost', 'port': 5001, 'neighbors': ['p1', 'p3']},
    'p3': {'host': 'localhost', 'port': 5002, 'neighbors': ['p2']},
}
```

## Quick Start

**Option 1: Manual startup**
```bash
# Terminal 1
python3 app.py p1

# Terminal 2  
python3 app.py p2

# Terminal 3
python3 app.py p3
```

**Option 2: Automated startup**
```bash
./Launcher.sh  # Uses tmux to launch all processes
```

## How It Works

1. **Message Creation** - Process creates message with Lamport timestamp
2. **Local Delivery** - Message processed locally first
3. **Flooding** - Message sent to all neighbor processes
4. **Propagation** - Neighbors forward message to their neighbors (excluding sender)
5. **Ordering** - All processes deliver messages in timestamp order

Messages are delivered consistently across all processes based on Lamport clock ordering, ensuring causal consistency in the distributed system.