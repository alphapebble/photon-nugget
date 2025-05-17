# Solar Sage Testing Guide

This document provides instructions for running tests and evaluations for the Solar Sage project.

## Table of Contents

- [Unit Tests](#unit-tests)
- [RAG Evaluation](#rag-evaluation)
- [Adding New Tests](#adding-new-tests)
- [Continuous Integration](#continuous-integration)

## Unit Tests

The Solar Sage project uses Python's built-in `unittest` framework for unit testing. Tests are organized in the `tests/unit` directory, with subdirectories for each major component.

### Running All Unit Tests

To run all unit tests, use the following command from the project root:

```bash
python -m unittest discover tests/unit
```

### Running Tests for Specific Components

To run tests for a specific component, use one of the following commands:

```bash
# Test agent components
python -m unittest discover tests/unit/agents

# Test RAG components
python -m unittest discover tests/unit/rag

# Test core components
python -m unittest discover tests/unit/core
```

### Running Individual Test Files

To run a specific test file, use the following command:

```bash
python -m unittest tests/unit/agents/test_tool_registry.py
```

### Running Tests with Proper Python Path

If you encounter import errors when running tests, make sure to set the Python path correctly:

```bash
PYTHONPATH=. python -m unittest discover tests/unit
```

## RAG Evaluation

The Solar Sage project includes a comprehensive RAG evaluation system in the `evaluation` directory. This system evaluates the quality of responses from the RAG system using various metrics.

### Running Basic Evaluation

To run a basic evaluation of the RAG system, use the following command:

```bash
python evaluation/evaluate.py
```

This will run the evaluation using the default settings and save the results in the `evaluation/results` directory.

### Running Evaluation with Custom Settings

You can customize the evaluation by modifying the parameters in the script or by importing the `evaluate` function in your own script:

```python
from evaluation.evaluate import evaluate

results = evaluate(
    csv_path="path/to/questions.csv",
    output_dir="path/to/output",
    use_dual_agent=True,
    include_weather=True,
    reference_answers_path="path/to/reference_answers.json"
)
```

### Evaluation Metrics

The evaluation system calculates the following metrics:

- **Keyword Match**: Percentage of expected keywords found in the response
- **Response Time**: Time taken to generate the response
- **Response Length**: Number of words in the response
- **BLEU Score**: Similarity between the response and reference answer
- **ROUGE Score**: Recall-oriented metric for evaluating text generation
- **Cosine Similarity**: Similarity between the response and reference answer

If RAGAS is installed, the following additional metrics are calculated:

- **Answer Relevancy**: How relevant the answer is to the question
- **Faithfulness**: Whether the answer is factually consistent with the context
- **Context Relevancy**: How relevant the retrieved contexts are to the question
- **Context Precision**: Precision of the retrieved contexts
- **Context Recall**: Recall of the retrieved contexts
- **Harmfulness**: Assessment of potential harmful content in the response

## Adding New Tests

### Adding Unit Tests

To add a new unit test, create a new file in the appropriate subdirectory of `tests/unit`. The file name should start with `test_` and should contain one or more test classes that inherit from `unittest.TestCase`.

Example:

```python
import unittest
from src.module_to_test import FunctionToTest

class TestMyFunction(unittest.TestCase):
    def setUp(self):
        # Set up test fixtures
        pass
        
    def test_basic_functionality(self):
        # Test basic functionality
        result = FunctionToTest(input_data)
        self.assertEqual(result, expected_output)
        
    def test_edge_case(self):
        # Test edge case
        result = FunctionToTest(edge_case_input)
        self.assertEqual(result, expected_edge_case_output)
```

### Adding Evaluation Questions

To add new evaluation questions, edit the `evaluation/eval_questions.csv` file. Each row should contain a question and the expected keywords in the answer.

Example:

```csv
question,expected_answer_keywords
How do solar panels work?,photovoltaic,semiconductor,electrons,sunlight,electricity
What affects solar panel efficiency?,temperature,shading,orientation,tilt,dust
```

### Adding Reference Answers

To add reference answers for advanced metrics, edit the `evaluation/reference_answers.json` file. Each key should be a question, and the value should be the reference answer.

Example:

```json
{
  "How do solar panels work?": "Solar panels work through the photovoltaic effect, where sunlight is converted into electricity by semiconductor materials. When sunlight hits the solar cells, it excites electrons, creating an electric current.",
  "What affects solar panel efficiency?": "Solar panel efficiency is affected by several factors including temperature, shading, orientation, tilt angle, and dust or dirt accumulation. Higher temperatures can reduce efficiency, while optimal orientation and tilt maximize sunlight exposure."
}
```

## Continuous Integration

The Solar Sage project uses GitHub Actions for continuous integration. Tests are automatically run on every push to the main branch and on every pull request.

### CI Workflow

The CI workflow is defined in `.github/workflows/ci.yml` and includes the following steps:

1. Set up Python environment
2. Install dependencies
3. Run unit tests
4. Run RAG evaluation (on a subset of questions)
5. Generate test reports

### Viewing Test Results

Test results are available in the GitHub Actions tab of the repository. For each workflow run, you can view the test results and download the test reports.

## Troubleshooting

### Import Errors

If you encounter import errors when running tests, make sure to set the Python path correctly:

```bash
PYTHONPATH=. python -m unittest discover tests/unit
```

### Missing Dependencies

If you encounter errors about missing dependencies, make sure to install all required packages:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development dependencies
```

### Test Database Not Found

Some tests require the LanceDB database to be present. If you see errors about missing databases, make sure to run the ingestion process first:

```bash
python scripts/ingest.py
```
