"""
Test runner for the dual-agent architecture tests.

This script runs all the unit tests for the dual-agent architecture components.
"""
import os
import sys
import unittest

# Add the project root and src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import test modules
from unit.agents.test_retriever_agent import TestRetrieverAgent
from unit.agents.test_response_generator_agent import TestResponseGeneratorAgent
from unit.agents.test_orchestrator import TestAgentOrchestrator
from unit.rag.test_rag_engine import TestRagEngine
from unit.rag.test_weather_enhanced_rag import TestWeatherEnhancedRag
from evaluation.test_rag_evaluation import TestRAGEvaluation

def run_tests():
    """Run all the dual-agent architecture tests."""
    # Create a test suite
    suite = unittest.TestSuite()

    # Create a test loader
    loader = unittest.TestLoader()

    # Add tests from the agents package
    suite.addTests(loader.loadTestsFromTestCase(TestRetrieverAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestResponseGeneratorAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentOrchestrator))

    # Add tests from the rag package
    suite.addTests(loader.loadTestsFromTestCase(TestRagEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestWeatherEnhancedRag))

    # Add evaluation tests (optional based on command line flag)
    include_eval = "--with-evaluation" in sys.argv
    if include_eval:
        print("Including RAG evaluation tests (may take longer to run)")
        suite.addTests(loader.loadTestsFromTestCase(TestRAGEvaluation))

    # Create a test runner
    runner = unittest.TextTestRunner(verbosity=2)

    # Run the tests
    print("\n" + "=" * 80)
    print(" DUAL-AGENT ARCHITECTURE TEST SUITE ".center(80, "="))
    print("=" * 80 + "\n")

    result = runner.run(suite)

    print("\n" + "=" * 80)
    print(" TEST RESULTS ".center(80, "="))
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 80 + "\n")

    return result

if __name__ == '__main__':
    result = run_tests()

    # Exit with non-zero code if there were failures or errors
    sys.exit(len(result.failures) + len(result.errors))
