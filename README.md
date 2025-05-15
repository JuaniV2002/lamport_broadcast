# Lamport Total-Order Broadcast Demo

A lightweight distributed chat/demo of the ISIS total-order broadcast algorithm using Lamport logical clocks. Perfect as a teaching aid or toy-project to explore ordering, synchronization and fault-tolerance in a peer-to-peer Python system.

## Features

- **Lamport Logical Clocks**  
  Each process maintains its own logical clock to timestamp events and enforce causality.

- **Total-Order Broadcast (ISIS Algorithm)**  
  Ensures every message is delivered in the same global order across all processes.

- **Proposal Collection with Timeout & Fallback**  
  Waits for proposals from all peers, but if one goes silent, proceeds after a configurable timeout.

- **Automatic Proposal Cleanup**  
  Clears out old proposal metadata to keep memory usage bounded.

- **Async Console I/O & Colorized Output**  
  Non-blocking input prompt, “chat” style display, and bright-cyan highlights for incoming messages.

- **Configurable Topology & Ports**  
  Define any number of peers in `config.py` (default toy size=2, but easily scaled to 10+).

- **IPv4 & LAN-Ready**  
  Binds to `0.0.0.0` for peer-to-peer over local networks; use `127.0.0.1` or LAN IPs.

---

## Requirements

- Python 3.6 or higher  
- Standard library modules only: `socket`, `threading`, `json`, `time`, `random`, `sys`

> No external dependencies — just clone and run.

---

## Configuration

1. **Define your peers** in `config.py`:
  ```python
  NUM_PROCESSES = 2
  BASE_PORT    = 5000

  PROCESSES = {
      'p1': {'host': '192.168.1.42', 'port': BASE_PORT},
      'p2': {'host': '192.168.1.37', 'port': BASE_PORT},
      # add more as needed...
  }
  ```
2. If you test on a single machine, set each host to 127.0.0.1 or use different LAN IPs for multi-host.
3. (Optional) Tweak the proposal timeout inside process.py:
  ```python
  timeout = 5.0  # seconds to wait for all proposals
  ```

---

## Quick start

1. Clone the repo.
2. Launch each peer in its own terminal:
   ```bash
   # Terminal 1
   python process.py p1

   # Terminal 2
   python process.py p2
   ```
3. Type messages in any terminal and watch them appear in all others, ordered correctly.
