"""Pre-defined scenarios for producer-consumer simulations."""

try:
    from .simulation import SimulationConfig
except ImportError:
    from simulation import SimulationConfig


SCENARIOS = {
    'balanced': SimulationConfig(
        scenario_name='balanced', num_producers=2, num_consumers=2,
        capacity=5, items_per_producer=10, producer_delay=0.1, consumer_delay=0.1
    ),
    'fast-producer': SimulationConfig(
        scenario_name='fast-producer', num_producers=2, num_consumers=1,
        capacity=3, items_per_producer=10, producer_delay=0.01, consumer_delay=0.2
    ),
    'fast-consumer': SimulationConfig(
        scenario_name='fast-consumer', num_producers=1, num_consumers=2,
        capacity=3, items_per_producer=10, producer_delay=0.2, consumer_delay=0.01
    ),
    'many-producers-few-consumers': SimulationConfig(
        scenario_name='many-producers-few-consumers', num_producers=5, num_consumers=1,
        capacity=5, items_per_producer=10, producer_delay=0.05, consumer_delay=0.1
    ),
    'high-contention': SimulationConfig(
        scenario_name='high-contention', num_producers=3, num_consumers=3,
        capacity=1, items_per_producer=20, producer_delay=0.05, consumer_delay=0.05
    ),
}


def get_scenario(name: str) -> SimulationConfig:
    if name not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {name}. Available: {', '.join(SCENARIOS.keys())}")
    return SCENARIOS[name]


def list_scenarios() -> dict:
    return {
        'balanced': 'Balanced workload - producers and consumers at similar speeds. Queue fluctuates but rarely full or empty.',
        'fast-producer': 'Fast producers, slow consumer. Demonstrates backpressure - producers frequently block when queue is full.',
        'fast-consumer': 'Slow producer, fast consumers. Demonstrates wait-on-empty - consumers frequently block waiting for items.',
        'many-producers-few-consumers': 'Multiple producers (5), single consumer. Stress tests synchronization and fairness.',
        'high-contention': 'Capacity=1 forces maximum context switching. Every put/take causes a thread to wake up.',
    }


def get_scenario_details() -> str:
    lines = ["Available Scenarios:", ""]
    for name, config in SCENARIOS.items():
        lines.extend([
            f"  {name}:",
            f"    {list_scenarios()[name]}",
            f"    Config: {config.num_producers}P/{config.num_consumers}C, capacity={config.capacity}, items_per_producer={config.items_per_producer}",
            f"    Delays: producer={config.producer_delay}s, consumer={config.consumer_delay}s",
            ""
        ])
    return "\n".join(lines)

