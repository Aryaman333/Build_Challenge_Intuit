"""
Producer-Consumer Mini Lab

A comprehensive implementation demonstrating concurrent programming concepts:
- Thread synchronization with locks and condition variables
- Blocking queues with wait/notify mechanism
- Multiple producer and consumer threads
- Various workload scenarios
"""

from .buffer import BoundedBuffer
from .producer import Producer
from .consumer import Consumer
from .simulation import Simulation, SimulationResult

__all__ = [
    'BoundedBuffer',
    'Producer',
    'Consumer',
    'Simulation',
    'SimulationResult'
]

__version__ = '1.0.0'
