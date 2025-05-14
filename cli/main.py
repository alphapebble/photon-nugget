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
        else:
            logger.error("No command specified")
            return 1
        
        return 0
    except Exception as e:
        logger.exception(f"Error running command: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
