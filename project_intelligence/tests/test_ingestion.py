import unittest
import os
from project_intelligence.ingestion.file_connector import FileConnector

class TestFileConnector(unittest.TestCase):
    def setUp(self):
        self.connector = FileConnector()
        # Construct the path to the sample document relative to this test file's location
        # __file__ is 'project_intelligence/tests/test_ingestion.py'
        # We want 'project_intelligence/sample_data/test_document.txt'
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # This should be the project_intelligence directory
        self.sample_file_path = os.path.join(base_dir, 'sample_data', 'test_document.txt')
        self.non_existent_file_path = os.path.join(base_dir, "non_existent_sample.txt")

    def test_fetch_data_reads_file_correctly(self):
        # Ensure the sample file exists for the test to run
        if not os.path.exists(self.sample_file_path):
            # Create a dummy file if it doesn't exist, to make test runnable in various environments
            # This is a fallback, ideally the file should be present.
            print(f"Warning: Sample file not found at {self.sample_file_path}. Creating a dummy for the test.")
            sample_dir = os.path.dirname(self.sample_file_path)
            if not os.path.exists(sample_dir):
                os.makedirs(sample_dir)
            with open(self.sample_file_path, 'w', encoding='utf-8') as f:
                f.write("Project Alpha is due next week. Task: implement feature X. Owner: Jules. Blocker: API access.")
        
        expected_content = "Project Alpha is due next week. Task: implement feature X. Owner: Jules. Blocker: API access."
        data = self.connector.fetch_data(self.sample_file_path)
        self.assertIsInstance(data, list, "fetch_data should return a list.")
        self.assertEqual(len(data), 1, "fetch_data should return a list with one element for this file.")
        self.assertEqual(data[0], expected_content, "The content of the fetched data does not match expected content.")

    def test_fetch_data_handles_file_not_found(self):
        # FileConnector's fetch_data currently prints an error and returns [] for FileNotFoundError
        # It does not raise FileNotFoundError itself.
        # To test this behavior, we check if an empty list is returned.
        
        # Ensure the non-existent file truly does not exist before the test
        if os.path.exists(self.non_existent_file_path):
            os.remove(self.non_existent_file_path)
            
        result = self.connector.fetch_data(self.non_existent_file_path)
        self.assertEqual(result, [], "fetch_data should return an empty list for a non-existent file.")

if __name__ == '__main__':
    unittest.main()
