"""
Connectors for the Project Intelligence System.

This module provides connectors for various data sources that the Project
Intelligence System can extract information from.
"""

from .base import DataSourceConnector
from .email import EmailConnector
from .slack import SlackConnector
from .spreadsheet import SpreadsheetConnector
from .teams import TeamsConnector

__all__ = [
    "DataSourceConnector",
    "EmailConnector",
    "SlackConnector",
    "SpreadsheetConnector",
    "TeamsConnector",
]