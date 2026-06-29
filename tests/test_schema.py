import json
import os
import unittest

class TestGlossarySchema(unittest.TestCase):
    def setUp(self):
        self.test_json_path = os.path.join(os.path.dirname(__file__), 'test_glossary.json')
        
    def test_json_validity(self):
        self.assertTrue(os.path.exists(self.test_json_path))
        with open(self.test_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Verify schema requirements per SKILL.md
        for term in data:
            self.assertIn("category", term)
            self.assertIn("term", term)
            self.assertIn("definition", term)
            self.assertIn("calculation_logic", term)
            self.assertIn("related_tables", term)
            self.assertIn("related_columns", term)
            
            # Check for Dataplex length constraints (term must be >= 2 characters if possible)
            display_name = term["term"].strip()
            self.assertGreaterEqual(len(display_name), 2, f"Term '{display_name}' length must be >= 2")

if __name__ == '__main__':
    unittest.main()
