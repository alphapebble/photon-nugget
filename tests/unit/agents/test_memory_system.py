"""
Unit tests for the Memory System.
"""
import os
import sys
import unittest
import tempfile
import json
import shutil
from datetime import datetime

# Add the project root and src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from agents.memory_system import MemorySystem

class TestMemorySystem(unittest.TestCase):
    """Test cases for the Memory System."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for memory storage
        self.temp_dir = tempfile.mkdtemp()
        self.memory_system = MemorySystem(storage_dir=self.temp_dir)
        
        # Test data
        self.user_id = "test_user"
        self.query = "How do solar panels work?"
        self.response = "Solar panels work by converting sunlight into electricity."
        self.tools_used = ["weather_tool", "production_tool"]
        self.context_used = "Solar panels are made of photovoltaic cells."

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)

    def test_add_interaction(self):
        """Test that interactions can be added to the memory."""
        # Add an interaction
        self.memory_system.add_interaction(
            user_id=self.user_id,
            query=self.query,
            response=self.response,
            tools_used=self.tools_used,
            context_used=self.context_used
        )
        
        # Check that the history file was created
        history_file = os.path.join(self.temp_dir, f"{self.user_id}_history.json")
        self.assertTrue(os.path.exists(history_file))
        
        # Check that the interaction was saved correctly
        with open(history_file, "r") as f:
            history = json.load(f)
        
        self.assertEqual(len(history), 1)
        interaction = history[0]
        self.assertEqual(interaction["query"], self.query)
        self.assertEqual(interaction["response"], self.response)
        self.assertEqual(interaction["tools_used"], self.tools_used)
        self.assertEqual(interaction["context_used"], self.context_used)
        self.assertIn("timestamp", interaction)

    def test_get_recent_interactions(self):
        """Test that recent interactions can be retrieved."""
        # Add multiple interactions
        for i in range(10):
            self.memory_system.add_interaction(
                user_id=self.user_id,
                query=f"Query {i}",
                response=f"Response {i}"
            )
        
        # Get recent interactions with default limit
        recent = self.memory_system.get_recent_interactions(self.user_id)
        self.assertEqual(len(recent), 5)  # Default limit is 5
        
        # Check that the most recent interactions are returned
        self.assertEqual(recent[-1]["query"], "Query 9")
        self.assertEqual(recent[-1]["response"], "Response 9")
        
        # Get recent interactions with custom limit
        recent = self.memory_system.get_recent_interactions(self.user_id, limit=3)
        self.assertEqual(len(recent), 3)
        
        # Check that the most recent interactions are returned
        self.assertEqual(recent[-1]["query"], "Query 9")
        self.assertEqual(recent[-1]["response"], "Response 9")

    def test_store_user_preference(self):
        """Test that user preferences can be stored."""
        # Store a preference
        self.memory_system.store_user_preference(
            user_id=self.user_id,
            preference_key="theme",
            preference_value="dark"
        )
        
        # Check that the preferences file was created
        prefs_file = os.path.join(self.temp_dir, f"{self.user_id}_preferences.json")
        self.assertTrue(os.path.exists(prefs_file))
        
        # Check that the preference was saved correctly
        with open(prefs_file, "r") as f:
            preferences = json.load(f)
        
        self.assertEqual(preferences["theme"], "dark")
        
        # Store another preference
        self.memory_system.store_user_preference(
            user_id=self.user_id,
            preference_key="language",
            preference_value="en"
        )
        
        # Check that both preferences are saved
        with open(prefs_file, "r") as f:
            preferences = json.load(f)
        
        self.assertEqual(preferences["theme"], "dark")
        self.assertEqual(preferences["language"], "en")

    def test_get_user_preference(self):
        """Test that user preferences can be retrieved."""
        # Store preferences
        self.memory_system.store_user_preference(
            user_id=self.user_id,
            preference_key="theme",
            preference_value="dark"
        )
        
        # Get an existing preference
        theme = self.memory_system.get_user_preference(
            user_id=self.user_id,
            preference_key="theme"
        )
        self.assertEqual(theme, "dark")
        
        # Get a non-existent preference with default value
        language = self.memory_system.get_user_preference(
            user_id=self.user_id,
            preference_key="language",
            default_value="en"
        )
        self.assertEqual(language, "en")
        
        # Get a preference for a non-existent user
        theme = self.memory_system.get_user_preference(
            user_id="non_existent_user",
            preference_key="theme",
            default_value="light"
        )
        self.assertEqual(theme, "light")

if __name__ == '__main__':
    unittest.main()
