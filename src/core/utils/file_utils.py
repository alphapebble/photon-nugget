"""
File utility functions for Solar Sage.

This module contains utility functions for working with files.
"""
import os
import json
from typing import Any, Dict, List, Optional, Union


def ensure_dir(directory: str) -> None:
    """
    Ensure a directory exists.
    
    Args:
        directory: Directory path
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def read_json(file_path: str) -> Dict[str, Any]:
    """
    Read a JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        JSON data as dictionary
        
    Raises:
        FileNotFoundError: If file not found
        json.JSONDecodeError: If file is not valid JSON
    """
    with open(file_path, "r") as f:
        return json.load(f)


def write_json(file_path: str, data: Union[Dict[str, Any], List[Any]]) -> None:
    """
    Write data to a JSON file.
    
    Args:
        file_path: Path to JSON file
        data: Data to write
    """
    # Ensure directory exists
    directory = os.path.dirname(file_path)
    if directory:
        ensure_dir(directory)
    
    # Write data
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def read_text(file_path: str) -> str:
    """
    Read a text file.
    
    Args:
        file_path: Path to text file
        
    Returns:
        File contents as string
        
    Raises:
        FileNotFoundError: If file not found
    """
    with open(file_path, "r") as f:
        return f.read()


def write_text(file_path: str, text: str) -> None:
    """
    Write text to a file.
    
    Args:
        file_path: Path to text file
        text: Text to write
    """
    # Ensure directory exists
    directory = os.path.dirname(file_path)
    if directory:
        ensure_dir(directory)
    
    # Write text
    with open(file_path, "w") as f:
        f.write(text)
