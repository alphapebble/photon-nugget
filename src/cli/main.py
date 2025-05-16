"""
Main CLI entry point for Solar Sage.

This module provides the main CLI entry point for the application.
"""
import argparse
import sys
from typing import List, Optional

from core.logging import setup_logging, get_logger
from cli.commands import (
    run_server,
    ingest_document,
    list_documents,
    run_ui,
    run_evaluation,
)

logger = get_logger(__name__)


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        args: Command-line arguments

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Solar Sage CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Server command
    server_parser = subparsers.add_parser("server", help="Run the API server")
    server_parser.add_argument("--host", help="Server host")
    server_parser.add_argument("--port", type=int, help="Server port")

    # UI command
    ui_parser = subparsers.add_parser("ui", help="Run the UI")
    ui_parser.add_argument("--port", type=int, help="UI port")
    ui_parser.add_argument("--mode", choices=["main", "evaluation"], default="main",
                         help="UI mode to run (main or evaluation)")
    ui_parser.add_argument("--share", action="store_true",
                         help="Create a public link for sharing")

    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest a document")
    ingest_parser.add_argument("source", help="Document source (file path or URL)")
    ingest_parser.add_argument("--db-path", help="Vector database path")
    ingest_parser.add_argument("--table", help="Vector database table")
    ingest_parser.add_argument("--model", help="Embedding model")
    ingest_parser.add_argument("--strategy", help="Chunking strategy")

    # List command
    list_parser = subparsers.add_parser("list", help="List ingested documents")
    list_parser.add_argument("--db-path", help="Vector database path")
    list_parser.add_argument("--table", help="Vector database table")

    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate RAG system")
    eval_parser.add_argument("--csv", default="evaluation/eval_questions.csv",
                           help="CSV file with evaluation questions")
    eval_parser.add_argument("--references", default="evaluation/reference_answers.json",
                           help="JSON file with reference answers")
    eval_parser.add_argument("--output-dir", default="evaluation/results",
                           help="Directory to save evaluation results")
    eval_parser.add_argument("--no-dual-agent", action="store_true",
                           help="Disable dual-agent architecture")
    eval_parser.add_argument("--weather", action="store_true",
                           help="Include weather context")

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point.

    Args:
        args: Command-line arguments

    Returns:
        Exit code
    """
    # Parse arguments
    parsed_args = parse_args(args)

    # Set up logging
    setup_logging()

    # Run command
    try:
        if parsed_args.command == "server":
            run_server(parsed_args)
        elif parsed_args.command == "ui":
            run_ui(parsed_args)
        elif parsed_args.command == "ingest":
            ingest_document(parsed_args)
        elif parsed_args.command == "list":
            list_documents(parsed_args)
        elif parsed_args.command == "evaluate":
            run_evaluation(parsed_args)
        else:
            logger.error("No command specified")
            return 1

        return 0
    except Exception as e:
        logger.exception(f"Error running command: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
