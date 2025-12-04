"""Thread-safe bounded buffer with explicit wait/notify mechanism."""

import threading
from typing import Any, Optional
from collections import deque


class BoundedBuffer:
    """Blocking queue using threading.Condition for wait/notify synchronization."""
    
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.buffer = deque()
        self.lock = threading.Lock()
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)
        self._total_put = 0
        self._total_take = 0
        self._max_size_reached = 0
        self._is_closed = False
    
    def put(self, item: Any, timeout: Optional[float] = None) -> bool:
        """Add item to buffer. Blocks if full. Returns False on timeout."""
        with self.not_full:
            if self._is_closed:
                raise RuntimeError("Buffer is closed")
            
            # Wait while full
            if timeout is None:
                while len(self.buffer) >= self.capacity:
                    self.not_full.wait()
            else:
                while len(self.buffer) >= self.capacity:
                    if not self.not_full.wait(timeout=timeout):
                        return False
            
            self.buffer.append(item)
            self._total_put += 1
            self._max_size_reached = max(self._max_size_reached, len(self.buffer))
            self.not_empty.notify()
            return True
    
    def take(self, timeout: Optional[float] = None) -> Optional[Any]:
        """Remove item from buffer. Blocks if empty. Returns None on timeout/closed."""
        with self.not_empty:
            # Wait while empty and not closed
            if timeout is None:
                while len(self.buffer) == 0 and not self._is_closed:
                    self.not_empty.wait()
            else:
                while len(self.buffer) == 0 and not self._is_closed:
                    if not self.not_empty.wait(timeout=timeout):
                        return None
            
            if len(self.buffer) == 0:
                return None
            
            item = self.buffer.popleft()
            self._total_take += 1
            self.not_full.notify()
            return item
    
    def size(self) -> int:
        with self.lock:
            return len(self.buffer)
    
    def is_full(self) -> bool:
        with self.lock:
            return len(self.buffer) >= self.capacity
    
    def is_empty(self) -> bool:
        with self.lock:
            return len(self.buffer) == 0
    
    def close(self):
        with self.lock:
            self._is_closed = True
            self.not_full.notify_all()
            self.not_empty.notify_all()
    
    def is_closed(self) -> bool:
        with self.lock:
            return self._is_closed
    
    def get_stats(self) -> dict:
        with self.lock:
            return {
                'total_put': self._total_put,
                'total_take': self._total_take,
                'max_size_reached': self._max_size_reached,
                'current_size': len(self.buffer),
                'capacity': self.capacity,
                'is_closed': self._is_closed
            }

