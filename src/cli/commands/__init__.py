"""
CLI commands for Solar Sage.

This module provides CLI commands for the application.
"""
import argparse
import os
from typing import Dict, Any

from core.config import get_config
from core.logging import get_logger

logger = get_logger(__name__)


def run_server(args: argparse.Namespace) -> None:
    """
    Run the API server.

    Args:
        args: Command-line arguments
    """
    from app.server import run_server as run_api_server

    host = args.host or get_config("api_host")
    port = args.port or int(get_config("api_port"))

    logger.info(f"Starting API server on {host}:{port}")
    run_api_server(host, port)


def run_ui(args: argparse.Namespace) -> None:
    """
    Run the UI.

    Args:
        args: Command-line arguments
    """
    from ui.app import run_ui as run_ui_server

    port = args.port or int(get_config("ui_port"))
    mode = args.mode if hasattr(args, 'mode') else "main"
    share = args.share if hasattr(args, 'share') else False

    logger.info(f"Starting UI in {mode} mode on port {port}")
    run_ui_server(port=port, share=share, mode=mode)


def ingest_document(args: argparse.Namespace) -> None:
    """
    Ingest a document.

    Args:
        args: Command-line arguments
    """
    from ingestion.enhanced_pipeline import run_pipeline

    db_path = args.db_path or get_config("vector_db_path")
    table = args.table or get_config("vector_db_table")
    model = args.model or get_config("embedding_model")
    strategy = args.strategy or get_config("default_chunk_strategy")

    logger.info(f"Ingesting document: {args.source}")
    success = run_pipeline(args.source, db_path, table, model, strategy)

    if success:
        logger.info("Document ingested successfully")
    else:
        logger.error("Failed to ingest document")


def list_documents(args: argparse.Namespace) -> None:
    """
    List ingested documents.

    Args:
        args: Command-line arguments
    """
    import lancedb

    db_path = args.db_path or get_config("vector_db_path")
    table_name = args.table or get_config("vector_db_table")

    logger.info(f"Listing documents in {db_path}/{table_name}")

    try:
        db = lancedb.connect(db_path)
        if table_name not in db.table_names():
            logger.error(f"Table {table_name} not found")
            return

        table = db.open_table(table_name)
        data = table.to_pandas()

        # Group by source document
        sources = data["doc_source"].unique()

        logger.info(f"Found {len(sources)} documents:")
        for source in sources:
            count = len(data[data["doc_source"] == source])
            logger.info(f"- {source}: {count} chunks")
    except Exception as e:
        logger.error(f"Error listing documents: {e}")


def run_evaluation(args: argparse.Namespace) -> None:
    """
    Run RAG system evaluation.

    Args:
        args: Command-line arguments
    """
    from evaluation.evaluate import evaluate

    csv_path = args.csv
    references_path = args.references
    output_dir = args.output_dir
    use_dual_agent = not args.no_dual_agent
    include_weather = args.weather

    # Check if files exist
    if not os.path.exists(csv_path):
        logger.error(f"Evaluation CSV file not found: {csv_path}")
        return

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    logger.info(f"Running RAG evaluation with questions from {csv_path}")
    logger.info(f"Using dual-agent: {use_dual_agent}, including weather: {include_weather}")

    try:
        # Run evaluation
        results = evaluate(
            csv_path=csv_path,
            output_dir=output_dir,
            use_dual_agent=use_dual_agent,
            include_weather=include_weather,
            reference_answers_path=references_path if os.path.exists(references_path) else None
        )

        # Log results summary
        logger.info(f"Evaluation complete. Processed {len(results)} questions.")
        logger.info(f"Results saved to {output_dir}")

        # Calculate and log average metrics
        if not results.empty:
            if "Keyword Match %" in results.columns:
                avg_match = results["Keyword Match %"].mean()
                logger.info(f"Average keyword match: {avg_match:.2f}%")

            if "Response Time (s)" in results.columns:
                avg_time = results["Response Time (s)"].mean()
                logger.info(f"Average response time: {avg_time:.3f} seconds")

            # Log RAGAS metrics if available
            ragas_cols = [col for col in results.columns if col.startswith("RAGAS ")]
            for col in ragas_cols:
                if col in results.columns:
                    avg_score = results[col].mean()
                    logger.info(f"Average {col}: {avg_score:.4f}")

        # Suggest viewing the evaluation dashboard
        logger.info("To view detailed results, run the evaluation dashboard:")
        logger.info("python -m cli.main ui --mode evaluation")

    except Exception as e:
        logger.error(f"Error running evaluation: {e}")
        import traceback
        logger.error(traceback.format_exc())
