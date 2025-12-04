# Intuit Build Challenge - Assignment 1

**Producer-Consumer Pattern Implementation with Thread Synchronization**

An implementation demonstrating concurrent programming concepts: thread synchronization, blocking queues, and wait/notify mechanisms through an interactive CLI.

---

## Quick Start

```bash
cd Assignment_1/producer_consumer

# Run a simulation
python cli.py simulate --scenario balanced

# Run tests
python cli.py test --suite all

# See all scenarios
python cli.py list
```

---

## Project Structure

```
Assignment_1/producer_consumer/
├── src/
│   ├── buffer.py          # BoundedBuffer: thread-safe queue with explicit wait/notify
│   ├── producer.py        # Producer: puts items into buffer, blocks when full
│   ├── consumer.py        # Consumer: takes items from buffer, blocks when empty
│   ├── simulation.py      # Simulation: orchestrates threads, collects results
│   └── scenarios.py       # 5 pre-defined scenarios (balanced, fast-producer, etc.)
├── tests/
│   ├── test_buffer.py            # 10 tests: blocking, capacity, wait/notify
│   ├── test_producer_consumer.py # 6 tests: data integrity, ordering, concurrency
│   └── test_scenarios.py         # 9 tests: integration, all scenarios
└── cli.py                 # Command-line interface (simulate/test modes)
```

---

## Core Implementation

### buffer.py - BoundedBuffer (Blocking Queue)
**Key Logic**:
- Uses `threading.Condition` for explicit wait/notify mechanism
- `put()`: Blocks when full via `not_full.wait()`, notifies consumers via `not_empty.notify()`
- `take()`: Blocks when empty via `not_empty.wait()`, notifies producers via `not_full.notify()`
- `threading.Lock` ensures thread-safe access to internal deque

**Testing Objectives Demonstrated**:
- **Thread Synchronization**: Lock protects all operations (lines 68-70, 109-111)
- **Blocking Queue**: Enforces capacity, blocks on full/empty (lines 84, 125)
- **Wait/Notify**: `Condition.wait()` releases lock and waits; `Condition.notify()` wakes threads (lines 84, 90, 125, 135)

### producer.py - Producer Thread
**Key Logic**:
- Reads items from source list and calls `buffer.put(item)`
- Blocks automatically when buffer is full (waits for consumer to take)
- Tracks statistics: items produced, blocks encountered

### consumer.py - Consumer Thread
**Key Logic**:
- Calls `buffer.take()` to retrieve items, stores in destination list
- Blocks automatically when buffer is empty (waits for producer to put)
- Uses timeout mechanism for graceful shutdown
- Tracks statistics: items consumed, waits encountered

### simulation.py - Orchestrator
**Key Logic**:
- Creates BoundedBuffer, producer threads, and consumer threads
- Manages thread lifecycle: start all → join producers → close buffer → join consumers
- Detects data loss/duplicates by comparing produced vs consumed item IDs
- Returns comprehensive results (throughput, blocks, waits, success/failure)

### scenarios.py - Pre-defined Scenarios
Five scenarios demonstrating different behaviors:
1. **balanced**: 2P/2C, similar speeds → queue fluctuates
2. **fast-producer**: 2P/1C, producers faster → backpressure, queue fills
3. **fast-consumer**: 1P/2C, consumers faster → queue empties
4. **many-producers-few-consumers**: 5P/1C → synchronization stress test
5. **high-contention**: 3P/3C, capacity=1 → maximum context switching

---

## Test Suites

### test_buffer.py (10 tests)
**What to Expect**:
- FIFO ordering verified in single-threaded test
- Capacity never exceeded with 3 concurrent producers
- `put()` blocks when full, `take()` blocks when empty
- `notify()` wakes exactly one waiting thread at a time
- `close()` wakes all waiting threads
- All tests PASS, no race conditions

**Key Test**: `test_blocking_behavior_when_full`
- Fills buffer to capacity, starts producer thread
- Producer blocks on `put()` until consumer calls `take()`
- Verifies wait mechanism works correctly

### test_producer_consumer.py (6 tests)
**What to Expect**:
- All produced items are consumed (no loss)
- Order preserved per producer (FIFO verified)
- No duplicates detected (set comparison)
- 3P/3C test with 60 items completes successfully
- Statistics tracked correctly

**Key Test**: `test_no_duplicates_no_loss`
- Produces 50 uniquely identified items
- Verifies len(consumed_ids) == len(set(consumed_ids)) (no duplicates)
- Verifies all IDs 0-49 consumed (no loss)

### test_scenarios.py (9 tests)
**What to Expect**:
- All 5 scenarios complete without deadlocks
- All scenarios show 0 data loss, 0 duplicates
- fast-producer shows producer blocks (backpressure)
- fast-consumer shows consumer waits (wait-on-empty)
- high-contention shows both blocks and waits (capacity=1)

**Total**: 25 tests, ~68 seconds runtime, 100% pass rate

---

## Concepts Demonstrated

### 1. Thread Synchronization
**Implementation**: `threading.Lock` acquired in all buffer operations via `with self.not_full:` and `with self.not_empty:`

**Evidence**: Multiple threads access shared buffer without race conditions. Test `test_capacity_never_exceeded_multi_thread` verifies no capacity violations.

### 2. Concurrent Programming
**Implementation**: Multiple producer and consumer threads run simultaneously, coordinated by shared buffer.

**Evidence**: `test_multiple_producers_multiple_consumers` runs 3P/3C with 60 items, all consumed correctly.

### 3. Blocking Queues
**Implementation**: `put()` blocks when `len(buffer) >= capacity`, `take()` blocks when `len(buffer) == 0`.

**Evidence**: Tests verify blocking behavior. Scenario `fast-producer` shows producers blocking 16 times.

### 4. Wait/Notify Mechanism
**Implementation**: 
```python
# Producer waits
while len(self.buffer) >= self.capacity:
    self.not_full.wait()  # Releases lock, waits for notify

# Consumer notifies
self.not_full.notify()  # Wakes one waiting producer
```

**Evidence**: Verbose mode shows "Waiting, queue is full..." messages. Test `test_notify_mechanism` verifies threads wake up correctly.

---

## CLI Usage

### Run Simulations
```bash
# Pre-defined scenario
python cli.py simulate --scenario balanced

# Verbose output (shows wait/notify in action)
python cli.py simulate --scenario fast-producer --verbose

# Custom configuration
python cli.py simulate --num-producers 5 --num-consumers 2 --capacity 10 --items 50
```

### Run Tests
```bash
python cli.py test --suite all          # All 25 tests
python cli.py test --suite buffer       # Buffer tests only
python cli.py test --suite scenarios    # Scenario integration tests
```

### List Scenarios
```bash
python cli.py list
```

---

## Expected Output

### Simulation (Summary)
```
======================================================================
Scenario: balanced
======================================================================

Results:
  Total produced: 20
  Total consumed: 20
  Items lost: 0
  Items duplicated: 0
  Max queue size reached: 2/5
  Simulation time: 1.008s
  Throughput: 19.84 items/sec
  Status: SUCCESS
```

### Simulation (Verbose)
```
[00.023s] [P0] Waiting, queue is full...
[00.202s] [C0] Consumed item={...}   | queue size: 2/3
[00.202s] [P0] Produced item={...}   | queue size: 3/3 (FULL, producers may block)
```

### Tests
```
Ran 25 tests in 67.651s
OK (All PASSED)

Scenario test output examples:
  Balanced: 20 items in 1.005s (19.90 items/sec)
  Fast-producer: 20 items in 4.009s, 16 producer blocks
  High-contention: 60 items in 1.010s, 16 blocks, 35 waits
```


## Performance

- **Throughput**: 10-60 items/sec depending on delays
- **Scalability**: Tested up to 10 producers + 10 consumers
- **Data Integrity**: 0 loss, 0 duplicates in all tests
- **Reliability**: 100% test pass rate, no deadlocks

---
