"""Unit Tests for Producer and Consumer Threads - No loss, order preservation, no duplicates."""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from buffer import BoundedBuffer
from producer import Producer
from consumer import Consumer


class TestProducerConsumer(unittest.TestCase):
    """Test producer and consumer thread behavior."""
    
    def test_all_produced_items_are_consumed(self):
        """Test that all items produced are eventually consumed."""
        buffer = BoundedBuffer(capacity=5)
        num_producers = 3
        items_per_producer = 10
        sources = [list(range(i * 100, i * 100 + items_per_producer)) for i in range(num_producers)]
        all_produced = [item for source in sources for item in source]
        consumed = []
        
        producers = [Producer(f"P{i}", sources[i], buffer, 0.01) for i in range(num_producers)]
        consumers = [Consumer(f"C{i}", buffer, consumed, None, 0.01, 0.5) for i in range(2)]
        
        for p in producers:
            p.start()
        for c in consumers:
            c.start()
        for p in producers:
            p.join()
        buffer.close()
        for c in consumers:
            c.join()
        
        self.assertEqual(len(consumed), len(all_produced))
        self.assertEqual(set(consumed), set(all_produced))
    
    def test_order_preserved_per_producer(self):
        """Test that items from each producer are consumed in order."""
        buffer = BoundedBuffer(capacity=10)
        source = [{'id': i, 'producer': 1} for i in range(10)]
        consumed = []
        
        producer = Producer("P1", source, buffer, 0.01)
        consumer = Consumer("C1", buffer, consumed, 10, 0.01)
        producer.start()
        consumer.start()
        producer.join()
        consumer.join()
        
        for i, item in enumerate(consumed):
            self.assertEqual(item['id'], i)
            self.assertEqual(item['producer'], 1)
    
    def test_no_duplicates_no_loss(self):
        """Test that items are neither duplicated nor lost."""
        buffer = BoundedBuffer(capacity=3)
        num_items = 50
        source = [{'id': i, 'value': f'item-{i}'} for i in range(num_items)]
        consumed = []
        
        producer = Producer("P1", source, buffer, 0.005)
        consumer = Consumer("C1", buffer, consumed, num_items, 0.01)
        producer.start()
        consumer.start()
        producer.join()
        consumer.join()
        
        consumed_ids = [item['id'] for item in consumed]
        self.assertEqual(len(consumed_ids), len(set(consumed_ids)))
        self.assertEqual(len(consumed_ids), num_items)
        self.assertEqual(set(consumed_ids), set(range(num_items)))
    
    def test_multiple_producers_multiple_consumers(self):
        """Test system with multiple producers and consumers."""
        buffer = BoundedBuffer(capacity=5)
        num_producers = 3
        num_consumers = 3
        items_per_producer = 20
        
        sources = [[{'producer_id': i, 'seq': j, 'unique_id': f'P{i}-{j}'} 
                   for j in range(items_per_producer)] for i in range(num_producers)]
        expected_items = [item['unique_id'] for source in sources for item in source]
        consumed = []
        
        producers = [Producer(f"P{i}", sources[i], buffer, 0.01) for i in range(num_producers)]
        consumers = [Consumer(f"C{i}", buffer, consumed, None, 0.01, 0.5) for i in range(num_consumers)]
        
        for p in producers:
            p.start()
        for c in consumers:
            c.start()
        for p in producers:
            p.join()
        buffer.close()
        for c in consumers:
            c.join()
        
        consumed_ids = [item['unique_id'] for item in consumed]
        self.assertEqual(len(consumed_ids), len(set(consumed_ids)))
        self.assertEqual(set(consumed_ids), set(expected_items))
        
        for i in range(num_producers):
            producer_items = [item for item in consumed if item['producer_id'] == i]
            for j, item in enumerate(producer_items):
                self.assertEqual(item['seq'], j)
    
    def test_producer_stats(self):
        """Test that producer statistics are tracked correctly."""
        buffer = BoundedBuffer(capacity=5)
        source = list(range(10))
        consumed = []
        
        producer = Producer("P1", source, buffer, 0.01)
        consumer = Consumer("C1", buffer, consumed, 10, 0.005)
        producer.start()
        consumer.start()
        producer.join()
        consumer.join()
        
        stats = producer.get_stats()
        self.assertEqual(stats['items_produced'], 10)
        self.assertEqual(stats['expected_items'], 10)
        self.assertIsNotNone(stats['duration'])
    
    def test_consumer_stats(self):
        """Test that consumer statistics are tracked correctly."""
        buffer = BoundedBuffer(capacity=5)
        source = list(range(10))
        consumed = []
        
        producer = Producer("P1", source, buffer, 0.005)
        consumer = Consumer("C1", buffer, consumed, 10, 0.01)
        producer.start()
        consumer.start()
        producer.join()
        consumer.join()
        
        stats = consumer.get_stats()
        self.assertEqual(stats['items_consumed'], 10)
        self.assertEqual(stats['expected_items'], 10)
        self.assertIsNotNone(stats['duration'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
