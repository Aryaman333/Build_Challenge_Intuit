# Quick Start Guide - Producer-Consumer 

## Installation

No installation required! Uses only Python standard library (Python 3.7+).

```bash
cd Assignment_1/producer_consumer
```

## Run Your First Simulation

```bash
# See available scenarios
python cli.py list

# Run balanced scenario
python cli.py simulate --scenario balanced

# See detailed logs
python cli.py simulate --scenario fast-producer --verbose
```

## Run Tests

```bash
# Run all tests (25 tests)
python cli.py test --suite all

# Run specific test suite
python cli.py test --suite buffer
python cli.py test --suite producer-consumer
python cli.py test --suite scenarios
```

## Create Custom Simulation

```bash
python cli.py simulate \
  --num-producers 5 \
  --num-consumers 2 \
  --capacity 10 \
  --items 50 \
  --producer-delay 0.05 \
  --consumer-delay 0.1 \
  --verbose
```

## Understanding the Output

### Summary Mode (Default)
Shows configuration and final results:
- Total items produced/consumed
- Items lost/duplicated (should be 0)
- Max queue size reached
- Throughput (items/sec)
- Success status

### Verbose Mode
Shows real-time event logs:
- Timestamps from simulation start
- Thread IDs (P0, P1, C0, C1, etc.)
- Queue size after each operation
- Waiting notifications (when threads block)

## Testing Objectives Demonstrated

1. **Thread Synchronization**: Lock protects all buffer access
2. **Concurrent Programming**: Multiple threads working together
3. **Blocking Queues**: put() blocks when full, take() blocks when empty
4. **Wait/Notify**: Explicit Condition.wait() and Condition.notify()

## Key Scenarios

- **balanced**: Normal workload, queue fluctuates
- **fast-producer**: Backpressure demonstration (queue fills up)
- **fast-consumer**: Wait-on-empty demonstration (queue empties)
- **many-producers-few-consumers**: Synchronization stress test
- **high-contention**: Maximum context switching (capacity=1)

## Expected Test Results

All 25 tests should PASS:
- 10 buffer tests (blocking, capacity, wait/notify)
- 6 producer-consumer tests (integrity, ordering)
- 9 scenario tests (integration, all scenarios)

Total runtime: ~60-70 seconds

## Next Steps

1. Study `src/buffer.py` to understand wait/notify implementation
2. Run scenarios in verbose mode to observe blocking behavior
3. Modify scenarios to test different configurations
4. Review test cases to understand verification approach
