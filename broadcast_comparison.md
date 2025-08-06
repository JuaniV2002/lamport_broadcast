# Flooding versus Two phase commit comparation for atomic broadcast implementation

## Two-Phase Commit

### Mechanics
- Message Types: request, reply, final
- How it works:
	1.	REQUEST: The initiator sends a request to all other processes for some event/value.
	2.	REPLY: Each process, upon receiving a request, sends a reply back to the initiator.
	3.	FINAL: After collecting all replies, the initiator broadcasts a final message to all, indicating the commit/delivery of the event.
- Key Properties:
	- Synchronization: No process delivers until it gets a final.
	- Coordination: The initiator acts as the coordinator.
	- Round trips: Two (request -> reply, then final).

### Pros
- Stronger Ordering: All processes deliver in the same order, and only after the coordinator says so.
- Determinism: All or none commit property; safer for strict atomicity.

### Cons
- High Latency: Two full message rounds per broadcast.
- Coordinator bottleneck: The initiator waits for all replies (if one process is slow, everyone waits).
- Message Complexity: For $N$ processes:
	- 1st phase: $(N-1)$ requests,$ (N-1)$ replies
	- 2nd phase: $N$ finals
	Total: $~3N-2$ messages per broadcast.

---

## Flooding

### Mechanics
- Message Propagation: When a process wants to broadcast, it sends the message to all others. Each receiver, if it hasn't seen the message, forwards it further. This continues until everyone has seen the message.
- No explicit phases (no "commit" round, no need to collect replies).
- Redundancy control: Typically, messages have unique IDs to avoid duplicates.

### Pros
- Lower Latency: As soon as a process receives the message, it can (typically) deliver or rebroadcast immediately.
- No Central Coordinator: No one waits for a “final” OK, system is less sensitive to individual slow processes.
- Message Complexity: At most $N(N-1)$ messages (if each process sends to all others), but actual delivery latency is 1 hop for directly connected, and a few hops for indirect ones.

### Cons
- Redundant messages: Some processes will see the same message multiple times.
- Weaker Ordering: If not using extra mechanisms, can be harder to guarantee total order or atomicity (unless paired with Lamport timestamps or similar).

---

## Comparative Table

<center>

| Aspect            | Two-Phase Commit                        | Flooding                                 |
|-------------------|-----------------------------------------|------------------------------------------|
| Atomicity         | Strong (all-or-nothing)                 | Can be strong if implemented carefully   |
| Ordering          | Strict, globally agreed                 | Weaker; needs extra logic for total order|
| Coordinator       | Yes (initiator is central)              | No central coordinator                   |
| Latency           | High (2 message rounds)                 | Low (1 round, best case)                 |
| Message Complexity| $~3N-2$ messages per broadcast          | Up to $N(N-1)$; often parallel           |
| Throughput        | Lower (coordinator bottleneck)          | Higher (parallel delivery)               |
| Fault Tolerance   | Low (coordinator is a single point)     | Higher (no single point of failure)      |
| Efficiency        | Lower for large $N$                     | Higher for small/medium $N$              |

</center>

---

## Why Flooding Is (Usually) More Efficient
- No need to wait for replies: Delivery is as fast as the slowest network hop, not the slowest process.
- No central coordinator: Eliminates the bottleneck, better parallelism.
- Less sensitive to process failures (as long as network is connected).

However, flooding can flood-meaning, if not carefully implemented, the network might be saturated with duplicate messages. But for small clusters or local processes, this isn't a big problem.

In our case, for local processes and modest scale, the flooding approach will nearly always outperform the two-phase approach in terms of latency and throughput. The only reason to pick the two-phase commit is if we need very strong, explicit atomicity and commit ordering, and can live with the performance hit.

---

## Summary
- Two-phase commit: Safe, deterministic, but slow and sensitive to bottlenecks.
- Flooding: Fast, robust, but needs care for order/duplication. Far more efficient in practice for local, small-scale atomic broadcast.
