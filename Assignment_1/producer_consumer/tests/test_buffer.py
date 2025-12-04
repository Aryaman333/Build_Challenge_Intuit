"""Unit Tests for BoundedBuffer - Thread synchronization, blocking queue, wait/notify."""

import unittest
import threading
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from buffer import BoundedBuffer


class TestBufferBasics(unittest.TestCase):
    """Test basic buffer operations."""
    
    def test_put_take_single_thread(self):
        """Test basic put/take in single thread - verifies FIFO order."""
        buffer = BoundedBuffer(capacity=5)
        items = [1, 2, 3, 4, 5]
        for item in items:
            self.assertTrue(buffer.put(item))
        for expected_item in items:
            self.assertEqual(buffer.take(), expected_item)
        self.assertTrue(buffer.is_empty())
        self.assertEqual(buffer.size(), 0)
    
    def test_capacity_never_exceeded(self):
        """Test that buffer never exceeds capacity."""
        capacity = 3
        buffer = BoundedBuffer(capacity=capacity)
        for i in range(capacity):
            buffer.put(i)
        self.assertTrue(buffer.is_full())
        self.assertEqual(buffer.size(), capacity)
        self.assertFalse(buffer.put(999, timeout=0.1))
        self.assertEqual(buffer.size(), capacity)
    
    def test_empty_buffer_blocks(self):
        """Test that take() blocks on empty buffer."""
        buffer = BoundedBuffer(capacity=5)
        self.assertIsNone(buffer.take(timeout=0.1))
    
    def test_buffer_stats(self):
        """Test that statistics are tracked correctly."""
        buffer = BoundedBuffer(capacity=5)
        for i in range(3):
            buffer.put(i)
        stats = buffer.get_stats()
        self.assertEqual(stats['total_put'], 3)
        self.assertEqual(stats['total_take'], 0)
        self.assertEqual(stats['current_size'], 3)
        self.assertEqual(stats['max_size_reached'], 3)
        buffer.take()
        buffer.take()
        stats = buffer.get_stats()
        self.assertEqual(stats['total_put'], 3)
        self.assertEqual(stats['total_take'], 2)
        self.assertEqual(stats['current_size'], 1)
        self.assertEqual(stats['max_size_reached'], 3)


class TestBufferConcurrency(unittest.TestCase):
    """Test buffer behavior under concurrent access."""
    
    def test_capacity_never_exceeded_multi_thread(self):
        """Test that capacity is never exceeded with multiple producer threads."""
        capacity = 5
        buffer = BoundedBuffer(capacity=capacity)
        num_producers = 3
        items_per_producer = 10
        violations = []
        consumed_items = []
        
        def producer_func():
            for i in range(items_per_producer):
                buffer.put(i)
                if buffer.size() > capacity:
                    violations.append(buffer.size())
                time.sleep(0.001)
        
        def consumer_func():
            while len(consumed_items) < num_producers * items_per_producer:
                item = buffer.take(timeout=0.5)
                if item is not None:
                    consumed_items.append(item)
                    time.sleep(0.001)
        
        consumer = threading.Thread(target=consumer_func)
        consumer.start()
        producers = [threading.Thread(target=producer_func) for _ in range(num_producers)]
        for p in producers:
            p.start()
        for p in producers:
            p.join()
        consumer.join(timeout=5.0)
        self.assertEqual(len(violations), 0, f"Capacity violations: {violations}")
        self.assertLessEqual(buffer.size(), capacity)
    
    def test_blocking_behavior_when_full(self):
        """Test that put() blocks when buffer is full."""
        capacity = 2
        buffer = BoundedBuffer(capacity=capacity)
        for i in range(capacity):
            buffer.put(i)
        put_completed = threading.Event()
        put_blocked = threading.Event()
        
        def blocked_producer():
            put_blocked.set()
            buffer.put(999)
            put_completed.set()
        
        producer = threading.Thread(target=blocked_producer)
        producer.start()
        put_blocked.wait(timeout=1.0)
        time.sleep(0.1)
        self.assertFalse(put_completed.is_set())
        buffer.take()
        put_completed.wait(timeout=1.0)
        self.assertTrue(put_completed.is_set())
        producer.join()
    
    def test_blocking_behavior_when_empty(self):
        """Test that take() blocks when buffer is empty."""
        buffer = BoundedBuffer(capacity=5)
        take_completed = threading.Event()
        take_blocked = threading.Event()
        result = []
        
        def blocked_consumer():
            take_blocked.set()
            result.append(buffer.take())
            take_completed.set()
        
        consumer = threading.Thread(target=blocked_consumer)
        consumer.start()
        take_blocked.wait(timeout=1.0)
        time.sleep(0.1)
        self.assertFalse(take_completed.is_set())
        buffer.put(42)
        take_completed.wait(timeout=1.0)
        self.assertTrue(take_completed.is_set())
        self.assertEqual(result[0], 42)
        consumer.join()
    
    def test_notify_mechanism(self):
        """Test that notify wakes up waiting threads."""
        buffer = BoundedBuffer(capacity=1)
        buffer.put(1)
        wake_count = []
        
        def waiting_producer(item):
            buffer.put(item)
            wake_count.append(1)
        
        producers = [threading.Thread(target=waiting_producer, args=(i,)) for i in range(3)]
        for p in producers:
            p.start()
        time.sleep(0.2)
        self.assertEqual(len(wake_count), 0)
        buffer.take()
        time.sleep(0.1)
        self.assertEqual(len(wake_count), 1)
        buffer.take()
        time.sleep(0.1)
        self.assertEqual(len(wake_count), 2)
        buffer.take()
        time.sleep(0.1)
        self.assertEqual(len(wake_count), 3)
        for p in producers:
            p.join()


class TestBufferClose(unittest.TestCase):
    """Test buffer close/shutdown behavior."""
    
    def test_close_wakes_waiting_threads(self):
        """Test that close() wakes up all waiting threads."""
        buffer = BoundedBuffer(capacity=5)
        results = []
        
        def waiting_consumer():
            results.append(buffer.take(timeout=5.0))
        
        consumers = [threading.Thread(target=waiting_consumer) for _ in range(3)]
        for c in consumers:
            c.start()
        time.sleep(0.2)
        buffer.close()
        for c in consumers:
            c.join(timeout=1.0)
            self.assertFalse(c.is_alive())
        self.assertEqual(len(results), 3)
        for item in results:
            self.assertIsNone(item)
    
    def test_put_after_close_raises_error(self):
        """Test that put() after close() raises error."""
        buffer = BoundedBuffer(capacity=5)
        buffer.close()
        with self.assertRaises(RuntimeError):
            buffer.put(1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
