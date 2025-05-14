"""
CLI commands for Solar Sage.

This module provides CLI commands for the application.
"""
import argparse
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
    
    logger.info(f"Starting UI on port {port}")
    run_ui_server(port)


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
