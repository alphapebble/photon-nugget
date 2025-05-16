"""
Tests for RAG evaluation.

This module provides a bridge between the specialized RAG evaluation in the evaluation/ 
directory and the standard test suite. It allows running RAG evaluation as part of the
test suite while keeping the specialized evaluation code separate.
"""
import os
import sys
import unittest
import json
import pandas as pd
from typing import Dict, Any, List, Optional

# Add the project root and src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Import the evaluation module
from evaluation.evaluate import evaluate, RAGEvaluator

class TestRAGEvaluation(unittest.TestCase):
    """Test case for RAG evaluation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.csv_path = "evaluation/eval_questions.csv"
        self.reference_answers_path = "evaluation/reference_answers.json"
        self.output_dir = "evaluation/results/test_run"
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def test_evaluator_initialization(self):
        """Test that the evaluator initializes correctly."""
        evaluator = RAGEvaluator(output_dir=self.output_dir)
        self.assertIsNotNone(evaluator)
        self.assertEqual(evaluator.output_dir, self.output_dir)
        self.assertIsNotNone(evaluator.orchestrator)
    
    def test_evaluation_with_basic_metrics(self):
        """Test evaluation with basic metrics."""
        # Skip if CSV file doesn't exist
        if not os.path.exists(self.csv_path):
            self.skipTest(f"Evaluation CSV file not found: {self.csv_path}")
        
        # Run evaluation with basic metrics only
        results = evaluate(
            csv_path=self.csv_path,
            output_dir=self.output_dir,
            use_dual_agent=True,
            include_weather=False,
            reference_answers_path=None  # Skip reference answers to use basic metrics only
        )
        
        # Check that results are returned
        self.assertIsInstance(results, pd.DataFrame)
        self.assertGreater(len(results), 0)
        
        # Check that basic metrics are included
        self.assertIn("Keyword Match %", results.columns)
        self.assertIn("Response Time (s)", results.columns)
        self.assertIn("Response Length", results.columns)
    
    @unittest.skipIf(not os.path.exists("evaluation/reference_answers.json"), 
                   "Reference answers file not found")
    def test_evaluation_with_reference_answers(self):
        """Test evaluation with reference answers."""
        # Run evaluation with reference answers
        results = evaluate(
            csv_path=self.csv_path,
            output_dir=self.output_dir,
            use_dual_agent=True,
            include_weather=False,
            reference_answers_path=self.reference_answers_path
        )
        
        # Check that results are returned
        self.assertIsInstance(results, pd.DataFrame)
        self.assertGreater(len(results), 0)
        
        # Check for advanced metrics columns (exact columns depend on available libraries)
        advanced_metrics_found = False
        for column in results.columns:
            if "BLEU" in column or "ROUGE" in column or "RAGAS" in column:
                advanced_metrics_found = True
                break
        
        # We should have at least some advanced metrics
        self.assertTrue(advanced_metrics_found, "No advanced metrics found in results")
    
    def test_summary_metrics_generation(self):
        """Test that summary metrics are generated."""
        # Skip if CSV file doesn't exist
        if not os.path.exists(self.csv_path):
            self.skipTest(f"Evaluation CSV file not found: {self.csv_path}")
        
        # Run evaluation
        evaluate(
            csv_path=self.csv_path,
            output_dir=self.output_dir,
            use_dual_agent=True,
            include_weather=False
        )
        
        # Check that summary metrics file was created
        summary_files = [f for f in os.listdir(self.output_dir) 
                       if f.startswith("summary_metrics_") and f.endswith(".json")]
        
        self.assertGreater(len(summary_files), 0, "No summary metrics files found")
        
        # Check content of the latest summary file
        latest_summary = sorted(summary_files)[-1]
        with open(os.path.join(self.output_dir, latest_summary), 'r') as f:
            summary = json.load(f)
        
        # Check basic structure
        self.assertIn("timestamp", summary)
        self.assertIn("num_questions", summary)
        self.assertIn("basic_metrics", summary)
        
        # Check basic metrics
        basic_metrics = summary["basic_metrics"]
        self.assertIn("avg_keyword_match", basic_metrics)
        self.assertIn("avg_response_time", basic_metrics)
        self.assertIn("avg_response_length", basic_metrics)

def run_evaluation_tests():
    """Run the RAG evaluation tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRAGEvaluation)
    return unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    run_evaluation_tests()
