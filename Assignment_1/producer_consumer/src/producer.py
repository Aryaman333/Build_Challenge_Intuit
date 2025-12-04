"""Producer thread that puts items into a bounded buffer."""

import threading
import time
from typing import List, Any, Optional, Callable


class Producer(threading.Thread):
    """Producer thread - reads from source and puts items into buffer."""
    
    def __init__(self, producer_id: str, source_container: List[Any], buffer,
                 delay: float = 0.0, verbose: bool = False, 
                 log_callback: Optional[Callable] = None):
        super().__init__(name=f"Producer-{producer_id}", daemon=True)
        self.producer_id = producer_id
        self.source_container = source_container
        self.buffer = buffer
        self.delay = delay
        self.verbose = verbose
        self.log_callback = log_callback
        self.items_produced = 0
        self.blocks_encountered = 0
        self.start_time = None
        self.end_time = None
    
    def _log(self, message: str):
        if self.verbose:
            if self.log_callback:
                self.log_callback(message)
            else:
                print(message, flush=True)
    
    def run(self):
        self.start_time = time.time()
        
        for item in self.source_container:
            try:
                was_full = self.buffer.is_full()
                if was_full:
                    self.blocks_encountered += 1
                    self._log(f"[{time.time() - self.start_time:06.3f}s] [{self.producer_id}] Waiting, queue is full...")
                
                self.buffer.put(item)
                self.items_produced += 1
                
                buffer_size = self.buffer.size()
                capacity = self.buffer.capacity
                status = "(FULL, producers may block)" if buffer_size == capacity else ""
                self._log(f"[{time.time() - self.start_time:06.3f}s] [{self.producer_id}] "
                         f"Produced item={item}   | queue size: {buffer_size}/{capacity} {status}")
                
                if self.delay > 0:
                    time.sleep(self.delay)
            except Exception as e:
                self._log(f"[{self.producer_id}] ERROR: {e}")
                break
        
        self.end_time = time.time()
        self._log(f"[{self.producer_id}] Finished. Produced {self.items_produced} items "
                 f"in {self.end_time - self.start_time:.3f}s (blocked {self.blocks_encountered} times)")
    
    def get_stats(self) -> dict:
        duration = self.end_time - self.start_time if self.start_time and self.end_time else None
        return {
            'producer_id': self.producer_id,
            'items_produced': self.items_produced,
            'blocks_encountered': self.blocks_encountered,
            'duration': duration,
            'expected_items': len(self.source_container)
        }

