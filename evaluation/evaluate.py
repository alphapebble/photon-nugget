import pandas as pd
import numpy as np
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional, Union
from collections import Counter

# Import RAG components
from rag.engines.base import rag_answer
from rag.engines.weather_enhanced import weather_enhanced_rag_answer
from agents.orchestrator import AgentOrchestrator

# Try to import RAGAS for specialized RAG evaluation
try:
    import ragas
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_relevancy,
        context_recall,
        context_precision
    )
    from ragas.metrics.critique import harmfulness
    import datasets
    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False
    print("RAGAS not available. Install with: pip install ragas")

# Fallback to basic NLP libraries if RAGAS is not available
try:
    import nltk
    from nltk.translate.bleu_score import sentence_bleu
    from nltk.tokenize import word_tokenize
    # Download necessary NLTK data
    nltk.download('punkt', quiet=True)
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    from rouge import Rouge
    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class RAGEvaluator:
    """Comprehensive evaluator for RAG systems."""

    def __init__(self, output_dir: str = "evaluation/results"):
        """Initialize the evaluator.

        Args:
            output_dir: Directory to save evaluation results
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.orchestrator = AgentOrchestrator()

        # Initialize metrics trackers
        self.metrics = {
            "keyword_match": [],
            "response_time": [],
            "response_length": [],
            "bleu_scores": [],
            "rouge_scores": [],
            "similarity_scores": []
        }

        # Track all results for detailed analysis
        self.all_results = []

    def evaluate_from_csv(self, csv_path: str, use_dual_agent: bool = True,
                         include_weather: bool = False,
                         reference_answers_path: Optional[str] = None) -> pd.DataFrame:
        """Evaluate RAG system using questions from a CSV file.

        Args:
            csv_path: Path to CSV with questions and expected keywords
            use_dual_agent: Whether to use the dual-agent architecture
            include_weather: Whether to include weather context
            reference_answers_path: Optional path to reference answers for BLEU/ROUGE

        Returns:
            DataFrame with evaluation results
        """
        print(f"Starting evaluation using {csv_path}...")
        df = pd.read_csv(csv_path)

        # Load reference answers if provided
        reference_answers = {}
        if reference_answers_path and os.path.exists(reference_answers_path):
            with open(reference_answers_path, 'r') as f:
                reference_answers = json.load(f)

        # Process each question
        for i, (_, row) in enumerate(df.iterrows()):
            question = row['question']
            expected_keywords = [kw.strip().lower() for kw in row['expected_answer_keywords'].split(',')]

            print(f"Processing question {i+1}/{len(df)}: {question}")

            # Get reference answer if available
            reference_answer = reference_answers.get(question, "")

            # Evaluate with the specified configuration
            self._evaluate_single_question(
                question=question,
                expected_keywords=expected_keywords,
                reference_answer=reference_answer,
                use_dual_agent=use_dual_agent,
                include_weather=include_weather
            )

        # Create results DataFrame
        results_df = pd.DataFrame(self.all_results)

        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_path = os.path.join(self.output_dir, f"evaluation_results_{timestamp}.csv")
        results_df.to_csv(results_path, index=False)

        # Save summary metrics
        self._save_summary_metrics(timestamp)

        print(f"Evaluation completed. Results saved to {results_path}")
        return results_df

    def _evaluate_single_question(self, question: str, expected_keywords: List[str],
                                reference_answer: str = "", use_dual_agent: bool = True,
                                include_weather: bool = False) -> Dict[str, Any]:
        """Evaluate a single question with comprehensive metrics.

        Args:
            question: The question to evaluate
            expected_keywords: List of expected keywords in the answer
            reference_answer: Reference answer for BLEU/ROUGE calculation
            use_dual_agent: Whether to use the dual-agent architecture
            include_weather: Whether to include weather context

        Returns:
            Dictionary with evaluation metrics
        """
        # Measure response time
        start_time = time.time()

        # Get response based on configuration
        if use_dual_agent:
            result = self.orchestrator.process_query(
                query=question,
                include_weather=include_weather
            )
            response = result['response']
            has_weather = result.get('has_weather_context', False)
            # Try to get retrieved contexts if available
            contexts = result.get('contexts', [])
        else:
            # Use basic RAG or weather-enhanced RAG
            if include_weather:
                contexts, response = weather_enhanced_rag_answer(question)
                has_weather = True
            else:
                contexts, response = rag_answer(question)
                has_weather = False

        # Calculate response time
        response_time = time.time() - start_time

        # Calculate basic metrics
        response_length = len(response.split())

        # Keyword match score
        keyword_matches = [kw for kw in expected_keywords if kw in response.lower()]
        match_score = len(keyword_matches)
        match_percent = (match_score / len(expected_keywords) * 100) if expected_keywords else 0

        # Create result dictionary with basic metrics
        result = {
            "Question": question,
            "Response": response,
            "Response Length": response_length,
            "Response Time (s)": round(response_time, 3),
            "Keyword Match %": round(match_percent, 2),
            "Matched Keywords": ", ".join(keyword_matches),
            "Expected Keywords": ", ".join(expected_keywords),
            "Used Dual Agent": use_dual_agent,
            "Included Weather": has_weather
        }

        # Store basic metrics
        self.metrics["keyword_match"].append(match_percent)
        self.metrics["response_time"].append(response_time)
        self.metrics["response_length"].append(response_length)

        # Use RAGAS for evaluation if available
        if RAGAS_AVAILABLE and reference_answer:
            ragas_metrics = self._calculate_ragas_metrics(
                question=question,
                answer=response,
                reference_answer=reference_answer,
                contexts=contexts
            )

            # Add RAGAS metrics to result
            for metric_name, metric_value in ragas_metrics.items():
                if metric_value is not None:
                    result[f"RAGAS {metric_name}"] = round(metric_value, 4)

                    # Store metrics for summary
                    if metric_name not in self.metrics:
                        self.metrics[metric_name] = []
                    self.metrics[metric_name].append(metric_value)

        # Fallback to basic NLP metrics if RAGAS is not available
        else:
            # Advanced metrics if libraries are available
            bleu_score = self._calculate_bleu(response, reference_answer) if NLTK_AVAILABLE and reference_answer else None
            rouge_scores = self._calculate_rouge(response, reference_answer) if ROUGE_AVAILABLE and reference_answer else None
            similarity_score = self._calculate_similarity(response, reference_answer) if SKLEARN_AVAILABLE and reference_answer else None

            # Store metrics
            if bleu_score is not None:
                self.metrics["bleu_scores"].append(bleu_score)
                result["BLEU Score"] = round(bleu_score, 4)

            if rouge_scores is not None:
                self.metrics["rouge_scores"].append(rouge_scores.get('rouge-1', {}).get('f', 0))
                result["ROUGE-1 F1"] = round(rouge_scores.get('rouge-1', {}).get('f', 0), 4)
                result["ROUGE-2 F1"] = round(rouge_scores.get('rouge-2', {}).get('f', 0), 4)
                result["ROUGE-L F1"] = round(rouge_scores.get('rouge-l', {}).get('f', 0), 4)

            if similarity_score is not None:
                self.metrics["similarity_scores"].append(similarity_score)
                result["Cosine Similarity"] = round(similarity_score, 4)

        # Add to all results
        self.all_results.append(result)

        return result

    def _calculate_ragas_metrics(self, question: str, answer: str,
                               reference_answer: str, contexts: List[str]) -> Dict[str, float]:
        """Calculate RAGAS metrics for RAG evaluation.

        Args:
            question: The question being evaluated
            answer: The generated answer
            reference_answer: The ground truth answer
            contexts: The contexts used to generate the answer

        Returns:
            Dictionary of RAGAS metrics
        """
        try:
            # Prepare data in RAGAS format
            data = {
                "question": [question],
                "answer": [answer],
                "ground_truth": [reference_answer]
            }

            # Add contexts if available
            if contexts:
                data["contexts"] = [contexts]

            # Convert to datasets format
            eval_dataset = datasets.Dataset.from_dict(data)

            # Calculate metrics
            metrics = {}

            # Answer relevancy (how relevant is the answer to the question)
            relevancy_score = answer_relevancy.compute(
                predictions=eval_dataset
            )
            metrics["Answer Relevancy"] = relevancy_score["answer_relevancy"][0]

            # Faithfulness (is the answer factually consistent with the context)
            if contexts:
                faithfulness_score = faithfulness.compute(
                    predictions=eval_dataset
                )
                metrics["Faithfulness"] = faithfulness_score["faithfulness"][0]

                # Context relevancy (how relevant are the retrieved contexts to the question)
                context_rel_score = context_relevancy.compute(
                    predictions=eval_dataset
                )
                metrics["Context Relevancy"] = context_rel_score["context_relevancy"][0]

                # Context precision and recall
                context_prec_score = context_precision.compute(
                    predictions=eval_dataset
                )
                metrics["Context Precision"] = context_prec_score["context_precision"][0]

                context_rec_score = context_recall.compute(
                    predictions=eval_dataset
                )
                metrics["Context Recall"] = context_rec_score["context_recall"][0]

            # Harmfulness assessment
            harm_score = harmfulness.compute(
                predictions=eval_dataset
            )
            metrics["Harmfulness"] = 1.0 - harm_score["harmfulness"][0]  # Invert so higher is better

            return metrics

        except Exception as e:
            print(f"Error calculating RAGAS metrics: {str(e)}")
            return {}

    def _calculate_bleu(self, candidate: str, reference: str) -> float:
        """Calculate BLEU score between candidate and reference."""
        if not candidate or not reference:
            return 0.0

        candidate_tokens = word_tokenize(candidate.lower())
        reference_tokens = [word_tokenize(reference.lower())]

        # Calculate BLEU score (with smoothing)
        try:
            return sentence_bleu(reference_tokens, candidate_tokens,
                               weights=(0.25, 0.25, 0.25, 0.25),
                               smoothing_function=nltk.translate.bleu_score.SmoothingFunction().method1)
        except Exception:
            return 0.0

    def _calculate_rouge(self, candidate: str, reference: str) -> Dict:
        """Calculate ROUGE scores between candidate and reference."""
        if not candidate or not reference:
            return {'rouge-1': {'f': 0}, 'rouge-2': {'f': 0}, 'rouge-l': {'f': 0}}

        try:
            rouge = Rouge()
            scores = rouge.get_scores(candidate, reference)[0]
            return scores
        except Exception:
            return {'rouge-1': {'f': 0}, 'rouge-2': {'f': 0}, 'rouge-l': {'f': 0}}

    def _calculate_similarity(self, candidate: str, reference: str) -> float:
        """Calculate cosine similarity between candidate and reference."""
        if not candidate or not reference:
            return 0.0

        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([candidate, reference])
            return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except Exception:
            return 0.0

    def _save_summary_metrics(self, timestamp: str) -> None:
        """Save summary metrics to a JSON file."""
        summary = {
            "timestamp": timestamp,
            "num_questions": len(self.all_results),
            "basic_metrics": {
                "avg_keyword_match": np.mean(self.metrics["keyword_match"]) if self.metrics["keyword_match"] else 0,
                "avg_response_time": np.mean(self.metrics["response_time"]) if self.metrics["response_time"] else 0,
                "avg_response_length": np.mean(self.metrics["response_length"]) if self.metrics["response_length"] else 0
            }
        }

        # Add RAGAS metrics if available
        if RAGAS_AVAILABLE:
            ragas_metrics = {}
            for metric_name in ["Answer Relevancy", "Faithfulness", "Context Relevancy",
                              "Context Precision", "Context Recall", "Harmfulness"]:
                if metric_name in self.metrics and self.metrics[metric_name]:
                    ragas_metrics[f"avg_{metric_name.lower().replace(' ', '_')}"] = np.mean(self.metrics[metric_name])

            if ragas_metrics:
                summary["ragas_metrics"] = ragas_metrics

        # Add fallback NLP metrics if used
        nlp_metrics = {}
        if "bleu_scores" in self.metrics and self.metrics["bleu_scores"]:
            nlp_metrics["avg_bleu_score"] = np.mean(self.metrics["bleu_scores"])
        if "rouge_scores" in self.metrics and self.metrics["rouge_scores"]:
            nlp_metrics["avg_rouge_score"] = np.mean(self.metrics["rouge_scores"])
        if "similarity_scores" in self.metrics and self.metrics["similarity_scores"]:
            nlp_metrics["avg_similarity_score"] = np.mean(self.metrics["similarity_scores"])

        if nlp_metrics:
            summary["nlp_metrics"] = nlp_metrics

        # Save metrics to file
        summary_path = os.path.join(self.output_dir, f"summary_metrics_{timestamp}.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        # Also save as CSV for easy import into visualization tools
        summary_flat = {
            "timestamp": timestamp,
            "num_questions": len(self.all_results),
            "avg_keyword_match": summary["basic_metrics"]["avg_keyword_match"],
            "avg_response_time": summary["basic_metrics"]["avg_response_time"],
            "avg_response_length": summary["basic_metrics"]["avg_response_length"]
        }

        # Add RAGAS metrics
        if "ragas_metrics" in summary:
            for k, v in summary["ragas_metrics"].items():
                summary_flat[k] = v

        # Add NLP metrics
        if "nlp_metrics" in summary:
            for k, v in summary["nlp_metrics"].items():
                summary_flat[k] = v

        # Save as CSV
        csv_path = os.path.join(self.output_dir, f"summary_metrics_{timestamp}.csv")
        pd.DataFrame([summary_flat]).to_csv(csv_path, index=False)

def evaluate(csv_path, output_dir="evaluation/results", use_dual_agent=True,
           include_weather=False, reference_answers_path=None):
    """Run evaluation on a CSV file of questions.

    Args:
        csv_path: Path to CSV with questions and expected keywords
        output_dir: Directory to save evaluation results
        use_dual_agent: Whether to use the dual-agent architecture
        include_weather: Whether to include weather context
        reference_answers_path: Optional path to reference answers for RAGAS metrics

    Returns:
        DataFrame with evaluation results
    """
    # Use default reference answers path if not provided
    if reference_answers_path is None:
        default_path = "evaluation/reference_answers.json"
        if os.path.exists(default_path):
            reference_answers_path = default_path

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Initialize evaluator and run evaluation
    evaluator = RAGEvaluator(output_dir=output_dir)
    return evaluator.evaluate_from_csv(
        csv_path=csv_path,
        use_dual_agent=use_dual_agent,
        include_weather=include_weather,
        reference_answers_path=reference_answers_path
    )

def generate_evaluation_report(results_dir="evaluation/results", latest=True):
    """Generate a comprehensive evaluation report from results.

    Args:
        results_dir: Directory containing evaluation results
        latest: Whether to use only the latest evaluation results

    Returns:
        HTML report as a string
    """
    # Find result files
    json_files = [f for f in os.listdir(results_dir) if f.startswith("summary_metrics_") and f.endswith(".json")]

    if not json_files:
        return "<p>No evaluation results found.</p>"

    # Sort by timestamp (newest first)
    json_files.sort(reverse=True)

    # Use only the latest file if requested
    if latest:
        json_files = [json_files[0]]

    # Load results
    all_results = []
    for json_file in json_files:
        with open(os.path.join(results_dir, json_file), 'r') as f:
            results = json.load(f)
            all_results.append(results)

    # Generate HTML report
    html = "<h2>RAG Evaluation Report</h2>"

    # Add summary table
    html += "<h3>Summary Metrics</h3>"
    html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
    html += "<tr><th>Timestamp</th><th>Questions</th><th>Keyword Match</th><th>Response Time</th>"

    # Add RAGAS metrics headers if available
    ragas_metrics = []
    for result in all_results:
        if "ragas_metrics" in result:
            for metric in result["ragas_metrics"].keys():
                if metric not in ragas_metrics:
                    ragas_metrics.append(metric)
                    html += f"<th>{metric.replace('avg_', '').replace('_', ' ').title()}</th>"

    html += "</tr>"

    # Add data rows
    for result in all_results:
        timestamp = result["timestamp"]
        num_questions = result["num_questions"]

        html += f"<tr><td>{timestamp}</td><td>{num_questions}</td>"
        html += f"<td>{result['basic_metrics']['avg_keyword_match']:.2f}%</td>"
        html += f"<td>{result['basic_metrics']['avg_response_time']:.3f}s</td>"

        # Add RAGAS metrics if available
        if "ragas_metrics" in result:
            for metric in ragas_metrics:
                if metric in result["ragas_metrics"]:
                    html += f"<td>{result['ragas_metrics'][metric]:.4f}</td>"
                else:
                    html += "<td>N/A</td>"

        html += "</tr>"

    html += "</table>"

    # Add visualization placeholders
    html += """
    <h3>Visualizations</h3>
    <div id="metrics-chart" style="width: 100%; height: 400px; margin-bottom: 20px; border: 1px solid #ddd;"></div>
    <div id="comparison-chart" style="width: 100%; height: 400px; border: 1px solid #ddd;"></div>

    <script>
        // Placeholder for charts - would be implemented in the UI
        document.getElementById('metrics-chart').innerHTML = 'Metrics chart will be displayed here';
        document.getElementById('comparison-chart').innerHTML = 'Comparison chart will be displayed here';
    </script>
    """

    return html

if __name__ == "__main__":
    # Run evaluation with default settings
    results = evaluate(
        csv_path="evaluation/eval_questions.csv",
        reference_answers_path="evaluation/reference_answers.json"
    )

    print(f"Evaluation complete. Found {len(results)} results.")
