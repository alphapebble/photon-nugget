"""
Evaluation Dashboard UI Component.

This module provides a Gradio UI for displaying RAG evaluation results.
"""
import os
import json
import pandas as pd
import numpy as np
import gradio as gr
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

from ui.config import (
    APP_TITLE,
    APP_DESCRIPTION,
    MODEL_INFO,
    KNOWLEDGE_INFO,
    GITHUB_LINK
)
from ui.template_loader import render_template, load_template, load_icon

def load_evaluation_results(results_dir: str = "evaluation/results") -> Tuple[List[Dict], pd.DataFrame]:
    """Load evaluation results from the specified directory.

    Args:
        results_dir: Directory containing evaluation results

    Returns:
        Tuple of (summary metrics list, detailed results DataFrame)
    """
    # Find summary metrics files
    json_files = [f for f in os.listdir(results_dir)
                if f.startswith("summary_metrics_") and f.endswith(".json")]

    if not json_files:
        return [], pd.DataFrame()

    # Sort by timestamp (newest first)
    json_files.sort(reverse=True)

    # Load summary metrics
    summary_metrics = []
    for json_file in json_files:
        with open(os.path.join(results_dir, json_file), 'r') as f:
            metrics = json.load(f)
            # Add file name for reference
            metrics["file_name"] = json_file
            summary_metrics.append(metrics)

    # Find detailed results files
    csv_files = [f for f in os.listdir(results_dir)
               if f.startswith("evaluation_results_") and f.endswith(".csv")]

    if not csv_files:
        return summary_metrics, pd.DataFrame()

    # Sort by timestamp (newest first)
    csv_files.sort(reverse=True)

    # Load the latest detailed results
    latest_csv = csv_files[0]
    detailed_results = pd.read_csv(os.path.join(results_dir, latest_csv))

    return summary_metrics, detailed_results

def create_metrics_chart(summary_metrics: List[Dict]) -> go.Figure:
    """Create a chart of evaluation metrics over time.

    Args:
        summary_metrics: List of summary metrics dictionaries

    Returns:
        Plotly figure
    """
    # Create a figure
    fig = go.Figure()

    if not summary_metrics:
        # Add annotation for empty data
        fig.add_annotation(
            text="No evaluation data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        # Set layout for empty chart
        fig.update_layout(
            title="Evaluation Metrics Over Time",
            xaxis_title="Evaluation Time",
            yaxis_title="Metric Value",
            height=400,
            template="plotly_white"
        )
        return fig

    # Extract timestamps and basic metrics
    data = []
    for metrics in summary_metrics:
        timestamp = metrics["timestamp"]

        # Basic metrics
        basic_metrics = metrics.get("basic_metrics", {})
        for metric_name, value in basic_metrics.items():
            data.append({
                "timestamp": timestamp,
                "metric": metric_name,
                "value": value,
                "category": "Basic"
            })

        # RAGAS metrics
        ragas_metrics = metrics.get("ragas_metrics", {})
        for metric_name, value in ragas_metrics.items():
            data.append({
                "timestamp": timestamp,
                "metric": metric_name,
                "value": value,
                "category": "RAGAS"
            })

        # NLP metrics
        nlp_metrics = metrics.get("nlp_metrics", {})
        for metric_name, value in nlp_metrics.items():
            data.append({
                "timestamp": timestamp,
                "metric": metric_name,
                "value": value,
                "category": "NLP"
            })

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Create figure
    fig = px.line(
        df,
        x="timestamp",
        y="value",
        color="metric",
        title="Evaluation Metrics Over Time",
        labels={"timestamp": "Evaluation Time", "value": "Metric Value"},
        hover_data=["category"]
    )

    # Improve layout
    fig.update_layout(
        legend_title="Metric",
        xaxis_title="Evaluation Time",
        yaxis_title="Metric Value",
        hovermode="closest"
    )

    return fig

def create_comparison_chart(detailed_results: pd.DataFrame) -> go.Figure:
    """Create a chart comparing different metrics across questions.

    Args:
        detailed_results: DataFrame of detailed evaluation results

    Returns:
        Plotly figure
    """
    # Create a figure
    fig = go.Figure()

    if detailed_results.empty:
        # Add annotation for empty data
        fig.add_annotation(
            text="No detailed evaluation data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        # Set layout for empty chart
        fig.update_layout(
            title="Metrics Comparison Across Questions",
            xaxis_title="Question",
            yaxis_title="Metric Value",
            height=400,
            template="plotly_white"
        )
        return fig

    # Select metrics to compare
    metrics = []

    # Always include keyword match if available
    if "Keyword Match %" in detailed_results.columns:
        metrics.append("Keyword Match %")

    # Add RAGAS metrics if available
    ragas_metrics = [col for col in detailed_results.columns if col.startswith("RAGAS ")]
    metrics.extend(ragas_metrics[:3])  # Limit to top 3 RAGAS metrics

    # Add BLEU/ROUGE if available and needed
    if len(metrics) < 4:
        if "BLEU Score" in detailed_results.columns:
            metrics.append("BLEU Score")
        if "ROUGE-1 F1" in detailed_results.columns:
            metrics.append("ROUGE-1 F1")

    # Ensure we have at least one metric
    if not metrics:
        # Create empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No metrics available for comparison",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

    # Prepare data for chart
    data = []
    for _, row in detailed_results.iterrows():
        question = row["Question"]
        # Truncate long questions
        if len(question) > 50:
            question = question[:47] + "..."

        for metric in metrics:
            if metric in row and not pd.isna(row[metric]):
                data.append({
                    "Question": question,
                    "Metric": metric,
                    "Value": row[metric]
                })

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Create figure
    fig = px.bar(
        df,
        x="Question",
        y="Value",
        color="Metric",
        barmode="group",
        title="Metrics Comparison Across Questions",
        labels={"Question": "Question", "Value": "Metric Value"}
    )

    # Improve layout
    fig.update_layout(
        legend_title="Metric",
        xaxis_title="Question",
        yaxis_title="Metric Value",
        hovermode="closest"
    )

    return fig

def create_evaluation_dashboard() -> gr.Blocks:
    """Create the evaluation dashboard UI.

    Returns:
        Gradio Blocks interface
    """
    # Load CSS from files
    css = load_template("css/simple.css")
    eval_css = load_template("css/evaluation.css")

    combined_css = css + eval_css

    with gr.Blocks(title=f"{APP_TITLE} - Evaluation Dashboard", css=combined_css) as dashboard:
        # Header with navigation
        gr.HTML(render_template("components/evaluation_header.html", {}))

        with gr.Row():
            with gr.Column():
                with gr.Group(elem_classes="metrics-container"):
                    refresh_btn = gr.Button("Refresh Data", variant="primary")
                    results_dir = gr.Textbox(
                        label="Results Directory",
                        value="evaluation/results",
                        info="Directory containing evaluation results"
                    )

                    # Summary metrics
                    summary_container = gr.HTML(
                        label="Summary Metrics",
                        value="<p>Click Refresh Data to load evaluation results.</p>"
                    )

        with gr.Row():
            # Metrics chart
            with gr.Group(elem_classes="chart-container"):
                gr.Markdown("### Metrics Over Time")
                metrics_chart = gr.Plot(
                    label="Metrics Over Time"
                )

        with gr.Row():
            # Comparison chart
            with gr.Group(elem_classes="chart-container"):
                gr.Markdown("### Metrics Comparison Across Questions")
                comparison_chart = gr.Plot(
                    label="Metrics Comparison"
                )

        with gr.Row():
            # Detailed results
            with gr.Accordion("Detailed Results", open=False):
                detailed_results = gr.DataFrame(
                    value=[],
                    headers=["Question", "Response Preview", "Keyword Match %", "Response Time (s)"],
                    interactive=False,
                    wrap=True
                )

        # Footer
        gr.HTML(f"""
        <div class="eval-footer">
            <p>{APP_TITLE} © {datetime.now().year} | <a href="{GITHUB_LINK}" target="_blank">GitHub</a></p>
        </div>
        """)

        # Function to update the dashboard
        def update_dashboard(results_dir):
            summary_metrics, detailed_df = load_evaluation_results(results_dir)

            if not summary_metrics:
                summary_html = "<p>No evaluation results found in the specified directory.</p>"
                return (
                    summary_html,
                    create_metrics_chart([]),
                    create_comparison_chart(pd.DataFrame()),
                    []
                )

            # Create summary HTML
            latest_metrics = summary_metrics[0]
            timestamp = latest_metrics["timestamp"]
            num_questions = latest_metrics["num_questions"]

            summary_html = f"<h3>Latest Evaluation: {timestamp}</h3>"
            summary_html += f"<p>Number of questions evaluated: {num_questions}</p>"

            # Add basic metrics
            summary_html += "<h4>Basic Metrics</h4>"
            summary_html += "<table style='width:100%; border-collapse: collapse;'>"
            summary_html += "<tr><th style='text-align:left; padding:8px; border:1px solid #ddd;'>Metric</th><th style='text-align:right; padding:8px; border:1px solid #ddd;'>Value</th></tr>"

            basic_metrics = latest_metrics.get("basic_metrics", {})
            for metric, value in basic_metrics.items():
                metric_name = metric.replace("avg_", "").replace("_", " ").title()
                summary_html += f"<tr><td style='text-align:left; padding:8px; border:1px solid #ddd;'>{metric_name}</td><td style='text-align:right; padding:8px; border:1px solid #ddd;'>{value:.4f}</td></tr>"

            summary_html += "</table>"

            # Add RAGAS metrics if available
            ragas_metrics = latest_metrics.get("ragas_metrics", {})
            if ragas_metrics:
                summary_html += "<h4>RAGAS Metrics</h4>"
                summary_html += "<table style='width:100%; border-collapse: collapse;'>"
                summary_html += "<tr><th style='text-align:left; padding:8px; border:1px solid #ddd;'>Metric</th><th style='text-align:right; padding:8px; border:1px solid #ddd;'>Value</th></tr>"

                for metric, value in ragas_metrics.items():
                    metric_name = metric.replace("avg_", "").replace("_", " ").title()
                    summary_html += f"<tr><td style='text-align:left; padding:8px; border:1px solid #ddd;'>{metric_name}</td><td style='text-align:right; padding:8px; border:1px solid #ddd;'>{value:.4f}</td></tr>"

                summary_html += "</table>"

            # Create charts
            metrics_fig = create_metrics_chart(summary_metrics)
            comparison_fig = create_comparison_chart(detailed_df)

            # Prepare detailed results for display
            if not detailed_df.empty:
                # Create a simple list of dictionaries with just the essential information
                simple_data = []

                for i, row in detailed_df.iterrows():
                    # Create a basic record with the question and key metrics
                    record = {
                        "Question": str(row["Question"]),
                        "Response Preview": str(row["Response"])[:100] + "..." if len(str(row["Response"])) > 100 else str(row["Response"]),
                        "Keyword Match %": f"{float(row['Keyword Match %']):.2f}%",
                        "Response Time (s)": f"{float(row['Response Time (s)']):.3f}s"
                    }
                    simple_data.append(record)

                detailed_display = simple_data
            else:
                # Create empty display with headers
                detailed_display = []

            return summary_html, metrics_fig, comparison_fig, detailed_display

        # Connect refresh button
        refresh_btn.click(
            fn=update_dashboard,
            inputs=[results_dir],
            outputs=[summary_container, metrics_chart, comparison_chart, detailed_results]
        )

        # Initial load
        dashboard.load(
            fn=update_dashboard,
            inputs=[results_dir],
            outputs=[summary_container, metrics_chart, comparison_chart, detailed_results]
        )

    return dashboard

if __name__ == "__main__":
    # Create and launch the dashboard
    dashboard = create_evaluation_dashboard()
    dashboard.launch(share=False)
