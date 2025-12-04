"""Command-Line Interface for Producer-Consumer Mini Lab."""

import argparse
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulation import Simulation, SimulationConfig
from src.scenarios import get_scenario, get_scenario_details, SCENARIOS


def simulate_command(args):
    if args.scenario:
        try:
            config = get_scenario(args.scenario)
            if args.verbose is not None:
                config.verbose = args.verbose
        except ValueError as e:
            print(f"Error: {e}\n")
            print(get_scenario_details())
            return 1
    else:
        config = SimulationConfig(
            scenario_name='custom',
            num_producers=args.num_producers,
            num_consumers=args.num_consumers,
            capacity=args.capacity,
            items_per_producer=args.items,
            producer_delay=args.producer_delay,
            consumer_delay=args.consumer_delay,
            verbose=args.verbose if args.verbose is not None else False
        )
    
    if not args.summary_only:
        print(f"\n{'=' * 70}\nScenario: {config.scenario_name}\n{'=' * 70}\n")
        print("Config:")
        print(f"  Producers: {config.num_producers}, Consumers: {config.num_consumers}")
        print(f"  Queue capacity: {config.capacity}")
        print(f"  Items per producer: {config.items_per_producer}")
        print(f"  Producer delay: {config.producer_delay}s, Consumer delay: {config.consumer_delay}s\n")
    
    result = Simulation(config).run()
    print(result.get_summary() if args.summary_only else result.get_summary())
    return 0 if result.success else 1


def test_command(args):
    tests_dir = Path(__file__).parent / 'tests'
    if not tests_dir.exists():
        print(f"Error: Tests directory not found at {tests_dir}")
        return 1
    
    sys.path.insert(0, str(tests_dir))
    loader = unittest.TestLoader()
    
    suite_map = {
        'all': ('test_*.py', "Running all tests..."),
        'buffer': ('test_buffer.py', "Running buffer tests..."),
        'producer-consumer': ('test_producer_consumer.py', "Running producer-consumer tests..."),
        'scenarios': ('test_scenarios.py', "Running scenario tests...")
    }
    
    if args.suite not in suite_map:
        print(f"Error: Unknown test suite: {args.suite}")
        print("Available suites: all, buffer, producer-consumer, scenarios")
        return 1
    
    pattern, message = suite_map[args.suite]
    print(message)
    suite = loader.discover(str(tests_dir), pattern=pattern)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def list_command(args):
    print(get_scenario_details())
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Producer-Consumer Mini Lab - Concurrent Programming Demonstrations'
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Simulate command
    sim = subparsers.add_parser('simulate', help='Run a producer-consumer simulation')
    sim.add_argument('--scenario', choices=list(SCENARIOS.keys()), help='Pre-defined scenario')
    sim.add_argument('--num-producers', type=int, default=2, help='Number of producers (default: 2)')
    sim.add_argument('--num-consumers', type=int, default=2, help='Number of consumers (default: 2)')
    sim.add_argument('--capacity', type=int, default=5, help='Queue capacity (default: 5)')
    sim.add_argument('--items', type=int, default=10, help='Items per producer (default: 10)')
    sim.add_argument('--producer-delay', type=float, default=0.1, help='Producer delay in seconds (default: 0.1)')
    sim.add_argument('--consumer-delay', type=float, default=0.1, help='Consumer delay in seconds (default: 0.1)')
    sim.add_argument('--verbose', action='store_true', help='Print detailed per-event logs')
    sim.add_argument('--summary-only', action='store_true', help='Only print summary')
    
    # Test command
    test = subparsers.add_parser('test', help='Run automated test suites')
    test.add_argument('--suite', choices=['all', 'buffer', 'producer-consumer', 'scenarios'], 
                     default='all', help='Test suite to run (default: all)')
    
    # List command
    subparsers.add_parser('list', help='List available scenarios')
    
    args = parser.parse_args()
    
    if args.command == 'simulate':
        return simulate_command(args)
    elif args.command == 'test':
        return test_command(args)
    elif args.command == 'list':
        return list_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())

