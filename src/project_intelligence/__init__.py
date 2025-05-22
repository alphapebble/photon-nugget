"""
Project Intelligence Layer for Solar-Sage

This module provides an AI-driven project intelligence layer that:
1. Parses emails, Slack/Teams messages, and spreadsheets in real-time
2. Detects project names, tasks, updates, owners, blockers, and due dates
3. Automatically maps these into a structured project dashboard
4. Monitors inventory, staffing, and overall progress without manual inputs
"""

from .core import ProjectIntelligenceSystem

__all__ = ["ProjectIntelligenceSystem"]