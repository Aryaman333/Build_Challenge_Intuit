"""Consumer thread that takes items from a bounded buffer."""

import threading
import time
from typing import List, Any, Optional, Callable


class Consumer(threading.Thread):
    """Consumer thread - takes items from buffer and stores in destination."""
    
    def __init__(self, consumer_id: str, buffer, destination_container: List[Any],
                 num_items: Optional[int] = None, delay: float = 0.0, 
                 verbose: bool = False, log_callback: Optional[Callable] = None, 
                 timeout: float = 1.0):
        super().__init__(name=f"Consumer-{consumer_id}", daemon=True)
        self.consumer_id = consumer_id
        self.buffer = buffer
        self.destination_container = destination_container
        self.num_items = num_items
        self.delay = delay
        self.verbose = verbose
        self.log_callback = log_callback
        self.timeout = timeout
        self._dest_lock = threading.Lock()
        self.items_consumed = 0
        self.waits_encountered = 0
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
        consecutive_timeouts = 0
        
        while True:
            if self.num_items and self.items_consumed >= self.num_items:
                break
            if self.buffer.is_closed() and self.buffer.is_empty():
                break
            
            try:
                was_empty = self.buffer.is_empty()
                if was_empty and not self.buffer.is_closed():
                    self.waits_encountered += 1
                    self._log(f"[{time.time() - self.start_time:06.3f}s] [{self.consumer_id}] Waiting, queue is empty...")
                
                item = self.buffer.take(timeout=self.timeout)
                
                if item is None:
                    consecutive_timeouts += 1
                    if consecutive_timeouts >= 3:
                        break
                    continue
                
                consecutive_timeouts = 0
                with self._dest_lock:
                    self.destination_container.append(item)
                self.items_consumed += 1
                
                buffer_size = self.buffer.size()
                capacity = self.buffer.capacity
                status = "(EMPTY, consumers may block)" if buffer_size == 0 else ""
                self._log(f"[{time.time() - self.start_time:06.3f}s] [{self.consumer_id}] "
                         f"Consumed item={item}   | queue size: {buffer_size}/{capacity} {status}")
                
                if self.delay > 0:
                    time.sleep(self.delay)
            except Exception as e:
                self._log(f"[{self.consumer_id}] ERROR: {e}")
                break
        
        self.end_time = time.time()
        self._log(f"[{self.consumer_id}] Finished. Consumed {self.items_consumed} items "
                 f"in {self.end_time - self.start_time:.3f}s (waited {self.waits_encountered} times)")
    
    def get_stats(self) -> dict:
        duration = self.end_time - self.start_time if self.start_time and self.end_time else None
        return {
            'consumer_id': self.consumer_id,
            'items_consumed': self.items_consumed,
            'waits_encountered': self.waits_encountered,
            'duration': duration,
            'expected_items': self.num_items
        }

