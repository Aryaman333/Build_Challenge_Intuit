"""Simulation orchestrator for producer-consumer scenarios."""

import time
import threading
from dataclasses import dataclass, field
from typing import List, Any, Dict, Optional, Callable

try:
    from .buffer import BoundedBuffer
    from .producer import Producer
    from .consumer import Consumer
except ImportError:
    from buffer import BoundedBuffer
    from producer import Producer
    from consumer import Consumer


@dataclass
class SimulationConfig:
    """Configuration for simulation."""
    num_producers: int = 2
    num_consumers: int = 2
    capacity: int = 5
    items_per_producer: int = 10
    producer_delay: float = 0.1
    consumer_delay: float = 0.1
    scenario_name: str = "custom"
    verbose: bool = False
    log_callback: Optional[Callable] = None
    timeout: float = 1.0
    
    def __post_init__(self):
        if self.num_producers <= 0 or self.num_consumers <= 0:
            raise ValueError("Producers and consumers must be positive")
        if self.capacity <= 0 or self.items_per_producer < 0:
            raise ValueError("Invalid capacity or items")


@dataclass
class SimulationResult:
    """Results from simulation."""
    scenario_name: str
    config: SimulationConfig
    start_time: float
    end_time: float
    duration: float
    total_produced: int
    total_consumed: int
    expected_total: int
    all_produced_items: List[Any] = field(default_factory=list)
    all_consumed_items: List[Any] = field(default_factory=list)
    max_queue_size: int = 0
    buffer_final_size: int = 0
    producer_stats: List[Dict] = field(default_factory=list)
    consumer_stats: List[Dict] = field(default_factory=list)
    items_lost: int = 0
    items_duplicated: int = 0
    errors: List[str] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        return (self.total_produced == self.expected_total and
                self.total_consumed == self.expected_total and
                self.items_lost == 0 and self.items_duplicated == 0 and
                len(self.errors) == 0)
    
    @property
    def throughput(self) -> float:
        return self.total_consumed / self.duration if self.duration > 0 else 0.0
    
    def get_summary(self) -> str:
        lines = [
            "", "=" * 70,
            f"Scenario: {self.scenario_name}",
            "=" * 70, "",
            "Configuration:",
            f"  Producers: {self.config.num_producers}, Consumers: {self.config.num_consumers}",
            f"  Queue capacity: {self.config.capacity}",
            f"  Items per producer: {self.config.items_per_producer}",
            f"  Producer delay: {self.config.producer_delay}s, Consumer delay: {self.config.consumer_delay}s",
            "", "Results:",
            f"  Total produced: {self.total_produced}",
            f"  Total consumed: {self.total_consumed}",
            f"  Items lost: {self.items_lost}",
            f"  Items duplicated: {self.items_duplicated}",
            f"  Max queue size reached: {self.max_queue_size}/{self.config.capacity}",
            f"  Simulation time: {self.duration:.3f}s",
            f"  Throughput: {self.throughput:.2f} items/sec",
            f"  Status: {'SUCCESS' if self.success else 'FAILURE'}",
            ""
        ]
        if self.errors:
            lines.extend(["Errors:"] + [f"  - {e}" for e in self.errors] + [""])
        lines.append("=" * 70)
        return "\n".join(lines)


class Simulation:
    """Orchestrates producer-consumer simulations."""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.buffer = None
        self.producers = []
        self.consumers = []
        self.produced_items = []
        self.consumed_items = []
        self._item_lock = threading.Lock()
    
    def _generate_items_for_producer(self, producer_id: int) -> List[Any]:
        items = []
        for i in range(self.config.items_per_producer):
            item = {
                'id': f"P{producer_id}-{i}",
                'producer': producer_id,
                'sequence': i,
                'data': f"Item {i} from producer {producer_id}"
            }
            items.append(item)
            with self._item_lock:
                self.produced_items.append(item)
        return items
    
    def run(self) -> SimulationResult:
        start_time = time.time()
        self.buffer = BoundedBuffer(self.config.capacity)
        
        # Create producers
        for i in range(self.config.num_producers):
            producer = Producer(
                producer_id=f"P{i}",
                source_container=self._generate_items_for_producer(i),
                buffer=self.buffer,
                delay=self.config.producer_delay,
                verbose=self.config.verbose,
                log_callback=self.config.log_callback
            )
            self.producers.append(producer)
        
        # Create consumers
        for i in range(self.config.num_consumers):
            consumer = Consumer(
                consumer_id=f"C{i}",
                buffer=self.buffer,
                destination_container=self.consumed_items,
                num_items=None,
                delay=self.config.consumer_delay,
                verbose=self.config.verbose,
                log_callback=self.config.log_callback,
                timeout=self.config.timeout
            )
            self.consumers.append(consumer)
        
        # Start all threads
        for p in self.producers:
            p.start()
        for c in self.consumers:
            c.start()
        
        # Wait for completion
        for p in self.producers:
            p.join()
        self.buffer.close()
        for c in self.consumers:
            c.join()
        
        return self._create_result(start_time, time.time())
    
    def _create_result(self, start_time: float, end_time: float) -> SimulationResult:
        total_produced = sum(p.items_produced for p in self.producers)
        total_consumed = sum(c.items_consumed for c in self.consumers)
        expected_total = self.config.num_producers * self.config.items_per_producer
        
        buffer_stats = self.buffer.get_stats()
        
        # Analyze items
        produced_ids = {item['id'] for item in self.produced_items}
        consumed_ids = [item['id'] for item in self.consumed_items]
        consumed_id_set = set(consumed_ids)
        
        items_lost = len(produced_ids - consumed_id_set)
        items_duplicated = len(consumed_ids) - len(consumed_id_set)
        
        errors = []
        unexpected = consumed_id_set - produced_ids
        if unexpected:
            errors.append(f"Found {len(unexpected)} items consumed but never produced")
        
        return SimulationResult(
            scenario_name=self.config.scenario_name,
            config=self.config,
            start_time=start_time,
            end_time=end_time,
            duration=end_time - start_time,
            total_produced=total_produced,
            total_consumed=total_consumed,
            expected_total=expected_total,
            all_produced_items=self.produced_items.copy(),
            all_consumed_items=self.consumed_items.copy(),
            max_queue_size=buffer_stats['max_size_reached'],
            buffer_final_size=buffer_stats['current_size'],
            producer_stats=[p.get_stats() for p in self.producers],
            consumer_stats=[c.get_stats() for c in self.consumers],
            items_lost=items_lost,
            items_duplicated=items_duplicated,
            errors=errors
        )

