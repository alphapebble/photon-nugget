import unittest
from project_intelligence.processing.entity_extractor import EntityExtractor

class TestEntityExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = EntityExtractor()
        self.sample_text = "This is a sample text for testing."

    def test_extract_entities_returns_dict_with_all_keys(self):
        extracted_data = self.extractor.extract_entities(self.sample_text)
        self.assertIsInstance(extracted_data, dict)
        expected_keys = ["project_names", "tasks", "updates", "owners", "blockers", "due_dates"]
        for key in expected_keys:
            self.assertIn(key, extracted_data)
            self.assertIsInstance(extracted_data[key], list)

    def test_placeholder_extraction_methods_return_empty_lists(self):
        # Test each private extraction method indirectly via extract_entities
        # or by calling them directly if you change their visibility for testing (not recommended for private methods)
        # For now, checking the output of extract_entities is sufficient.
        extracted_data = self.extractor.extract_entities(self.sample_text)
        self.assertEqual(extracted_data["project_names"], [])
        self.assertEqual(extracted_data["tasks"], [])
        self.assertEqual(extracted_data["updates"], [])
        self.assertEqual(extracted_data["owners"], [])
        self.assertEqual(extracted_data["blockers"], [])
        self.assertEqual(extracted_data["due_dates"], [])

if __name__ == '__main__':
    unittest.main()
