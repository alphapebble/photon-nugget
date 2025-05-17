"""
Memory System for Solar Sage Agent.

This module manages conversation history and user preferences.
"""
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime


class MemorySystem:
    """Memory system for agent conversations and user preferences."""

    def __init__(self, storage_dir: str = "./data/memory"):
        """
        Initialize the memory system.

        Args:
            storage_dir: Directory to store memory files
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def _get_user_file(self, user_id: str, file_type: str) -> str:
        """Get the path to a user's file."""
        return os.path.join(self.storage_dir, f"{user_id}_{file_type}.json")

    def add_interaction(
        self,
        user_id: str,
        query: str,
        response: str,
        tools_used: Optional[List[str]] = None,
        context_used: Optional[str] = None
    ) -> None:
        """
        Add a new interaction to the user's history.

        Args:
            user_id: User identifier
            query: User's query
            response: System's response
            tools_used: List of tools used in the interaction
            context_used: Context information used for the response
        """
        # TODO: Implement adding an interaction to the user's history
        # 1. Get the user's history file path
        # 2. Load existing history or create a new one
        # 3. Add the new interaction with timestamp
        # 4. Save the updated history
        # Example implementation:
        history_file = self._get_user_file(user_id, "history")

        # Load existing history or create new
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                history = json.load(f)
        else:
            history = []

        # Add new interaction
        history.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "tools_used": tools_used or [],
            "context_used": context_used
        })

        # Save updated history
        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)

    def get_recent_interactions(
        self,
        user_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get recent interactions for a user.

        Args:
            user_id: User identifier
            limit: Maximum number of interactions to return

        Returns:
            List of recent interactions
        """
        # TODO: Implement retrieving recent interactions
        # 1. Get the user's history file path
        # 2. Load the history if it exists
        # 3. Return the most recent interactions up to the limit
        # Example implementation:
        history_file = self._get_user_file(user_id, "history")

        if not os.path.exists(history_file):
            return []

        with open(history_file, "r") as f:
            history = json.load(f)

        return history[-limit:]

    def store_user_preference(
        self,
        user_id: str,
        preference_key: str,
        preference_value: Any
    ) -> None:
        """
        Store a user preference.

        Args:
            user_id: User identifier
            preference_key: Preference name
            preference_value: Preference value
        """
        # TODO: Implement storing a user preference
        # 1. Get the user's preferences file path
        # 2. Load existing preferences or create a new one
        # 3. Update the preference
        # 4. Save the updated preferences
        # Example implementation:
        prefs_file = self._get_user_file(user_id, "preferences")

        # Load existing preferences or create new
        if os.path.exists(prefs_file):
            with open(prefs_file, "r") as f:
                preferences = json.load(f)
        else:
            preferences = {}

        # Update preference
        preferences[preference_key] = preference_value

        # Save updated preferences
        with open(prefs_file, "w") as f:
            json.dump(preferences, f, indent=2)

    def get_user_preference(
        self,
        user_id: str,
        preference_key: str,
        default_value: Any = None
    ) -> Any:
        """
        Get a user preference.

        Args:
            user_id: User identifier
            preference_key: Preference name
            default_value: Default value if preference not found

        Returns:
            Preference value or default
        """
        # TODO: Implement retrieving a user preference
        # 1. Get the user's preferences file path
        # 2. Load the preferences if they exist
        # 3. Return the preference value or the default
        # Example implementation:
        prefs_file = self._get_user_file(user_id, "preferences")

        if not os.path.exists(prefs_file):
            return default_value

        with open(prefs_file, "r") as f:
            preferences = json.load(f)

        return preferences.get(preference_key, default_value)
