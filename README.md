# Distributed Message Broadcast with Lamport Clocks

A simple distributed chat system using UDP message flooding and Lamport logical clocks for message ordering.

## Overview

This project demonstrates inter-process communication (IPC) in a distributed system where multiple processes communicate through a neighbor-based network topology. Messages are flooded across the network and delivered in a consistent order using Lamport timestamps.

## Features

- **UDP-based communication** between processes
- **Message flooding** through configurable neighbor topology
- **Lamport clocks** for causal message ordering
- **Duplicate detection** to prevent message re-delivery

## Requirements

- Python 3.7+
- tmux (optional, for automated multi-process launch)

## Usage

### Manual Launch

```bash
cd src

# Start each process in a separate terminal
python3 app.py p1
python3 app.py p2
python3 app.py p3
```

### Automated Launch (tmux)

```bash
cd src
./Launcher.sh
```

Type a message in any process terminal to broadcast it to all other processes.

## Configuration

Edit `src/config.py` to modify the network topology:

```python
PROCESSES = {
    'p1': {'host': 'localhost', 'port': 5000, 'neighbors': ['p2']},
    'p2': {'host': 'localhost', 'port': 5001, 'neighbors': ['p1', 'p3']},
    'p3': {'host': 'localhost', 'port': 5002, 'neighbors': ['p2']},
}
```

## Project Structure

```
src/
├── app.py         # Entry point
├── Process.py     # Core process logic (networking, flooding, ordering)
├── config.py      # Network topology definition
└── Launcher.sh    # tmux launcher script
```

## How It Works

1. Each process listens on a UDP port and connects to its defined neighbors
2. When a user sends a message, it's assigned a Lamport timestamp and flooded to neighbors
3. Each receiving process updates its clock, forwards the message to other neighbors, and queues it for delivery
4. Messages are delivered in timestamp order (ties broken by sender ID)