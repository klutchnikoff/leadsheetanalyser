#!/usr/bin/env python3
"""
Test runner for leadsheetanalyser package.

Run this script to execute all tests for the leadsheetanalyser package.
"""
import sys
import unittest
import os

# Add the package to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_tests():
    """Run all tests in the tests directory."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

def run_specific_module(module_name):
    """Run tests for a specific module."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f'test_{module_name}')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific test module
        module = sys.argv[1]
        exit_code = run_specific_module(module)
    else:
        # Run all tests
        print("Running all leadsheetanalyser tests...")
        print("=" * 50)
        exit_code = run_all_tests()
    
    sys.exit(exit_code)
