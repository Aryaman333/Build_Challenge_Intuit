"""Integration Tests for Pre-defined Scenarios - Data integrity and deadlock-free completion."""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from simulation import Simulation
from scenarios import SCENARIOS, get_scenario


class TestScenarios(unittest.TestCase):
    """Test all pre-defined scenarios."""
    
    def test_balanced_scenario(self):
        """Test balanced scenario."""
        config = get_scenario('balanced')
        result = Simulation(config).run()
        self.assertTrue(result.success, f"Errors: {result.errors}")
        self.assertEqual(result.items_lost, 0)
        self.assertEqual(result.items_duplicated, 0)
        self.assertEqual(result.total_produced, result.expected_total)
        self.assertEqual(result.total_consumed, result.expected_total)
        self.assertLess(result.duration, 5.0)
        print(f"\nBalanced: {result.total_consumed} items in {result.duration:.3f}s ({result.throughput:.2f} items/sec)")
    
    def test_fast_producer_scenario(self):
        """Test fast-producer scenario - demonstrates backpressure."""
        config = get_scenario('fast-producer')
        result = Simulation(config).run()
        self.assertTrue(result.success, f"Errors: {result.errors}")
        self.assertEqual(result.items_lost, 0)
        self.assertEqual(result.items_duplicated, 0)
        self.assertEqual(result.max_queue_size, config.capacity)
        total_blocks = sum(p['blocks_encountered'] for p in result.producer_stats)
        self.assertGreater(total_blocks, 0, "Producers should have blocked")
        self.assertLess(result.duration, 5.0)
        print(f"\nFast-producer: {result.total_consumed} items in {result.duration:.3f}s, {total_blocks} producer blocks")
    
    def test_fast_consumer_scenario(self):
        """Test fast-consumer scenario - demonstrates wait-on-empty."""
        config = get_scenario('fast-consumer')
        result = Simulation(config).run()
        self.assertTrue(result.success, f"Errors: {result.errors}")
        self.assertEqual(result.items_lost, 0)
        self.assertEqual(result.items_duplicated, 0)
        total_waits = sum(c['waits_encountered'] for c in result.consumer_stats)
        self.assertGreater(total_waits, 0, "Consumers should have waited")
        self.assertLess(result.duration, 5.0)
        print(f"\nFast-consumer: {result.total_consumed} items in {result.duration:.3f}s, {total_waits} consumer waits")
    
    def test_many_producers_few_consumers_scenario(self):
        """Test many-producers-few-consumers scenario - stress test synchronization."""
        config = get_scenario('many-producers-few-consumers')
        result = Simulation(config).run()
        self.assertTrue(result.success, f"Errors: {result.errors}")
        self.assertEqual(result.items_lost, 0)
        self.assertEqual(result.items_duplicated, 0)
        self.assertEqual(len(result.producer_stats), 5)
        for p_stat in result.producer_stats:
            self.assertEqual(p_stat['items_produced'], p_stat['expected_items'])
        self.assertLess(result.duration, 10.0)
        print(f"\nMany-producers: {result.total_consumed} items in {result.duration:.3f}s ({result.throughput:.2f} items/sec)")
    
    def test_high_contention_scenario(self):
        """Test high-contention scenario - capacity=1 forces maximum context switching."""
        config = get_scenario('high-contention')
        result = Simulation(config).run()
        self.assertTrue(result.success, f"Errors: {result.errors}")
        self.assertEqual(result.items_lost, 0)
        self.assertEqual(result.items_duplicated, 0)
        self.assertEqual(config.capacity, 1)
        self.assertEqual(result.max_queue_size, 1)
        total_blocks = sum(p['blocks_encountered'] for p in result.producer_stats)
        total_waits = sum(c['waits_encountered'] for c in result.consumer_stats)
        self.assertGreater(total_blocks, 0, "Producers should have blocked")
        self.assertGreater(total_waits, 0, "Consumers should have waited")
        self.assertLess(result.duration, 10.0)
        print(f"\nHigh-contention: {result.total_consumed} items in {result.duration:.3f}s, {total_blocks} blocks, {total_waits} waits")
    
    def test_all_scenarios_complete(self):
        """Test that all scenarios can complete without hanging."""
        for scenario_name in SCENARIOS.keys():
            with self.subTest(scenario=scenario_name):
                config = get_scenario(scenario_name)
                result = Simulation(config).run()
                self.assertTrue(result.success, f"{scenario_name} failed: {result.errors}")
                self.assertLess(result.duration, 10.0, f"{scenario_name} took too long: {result.duration}s")


class TestScenarioIntegrity(unittest.TestCase):
    """Test data integrity across scenarios."""
    
    def test_no_data_loss_in_any_scenario(self):
        """Verify no data loss in any scenario."""
        for scenario_name in SCENARIOS.keys():
            with self.subTest(scenario=scenario_name):
                result = Simulation(get_scenario(scenario_name)).run()
                self.assertEqual(result.items_lost, 0, f"{scenario_name} lost items")
    
    def test_no_duplicates_in_any_scenario(self):
        """Verify no duplicates in any scenario."""
        for scenario_name in SCENARIOS.keys():
            with self.subTest(scenario=scenario_name):
                result = Simulation(get_scenario(scenario_name)).run()
                self.assertEqual(result.items_duplicated, 0, f"{scenario_name} duplicated items")
    
    def test_production_equals_consumption(self):
        """Verify production equals consumption in all scenarios."""
        for scenario_name in SCENARIOS.keys():
            with self.subTest(scenario=scenario_name):
                result = Simulation(get_scenario(scenario_name)).run()
                self.assertEqual(result.total_produced, result.total_consumed, f"{scenario_name}: production != consumption")


if __name__ == '__main__':
    unittest.main(verbosity=2)
