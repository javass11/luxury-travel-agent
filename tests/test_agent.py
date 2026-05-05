import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import LuxuryTravelDB
from src.agent import LuxuryTravelAssistant


class TestLuxuryTravelAssistant(unittest.TestCase):
    def setUp(self):
        self.db = LuxuryTravelDB(":memory:")
        self.assistant = LuxuryTravelAssistant(self.db)

    def tearDown(self):
        self.db.close()

    def test_assistant_initialization(self):
        self.assertIsNotNone(self.assistant)
        self.assertEqual(len(self.assistant.conversation_history), 0)

    def test_clear_history(self):
        self.assistant.conversation_history = [
            {"role": "user", "content": "test"},
            {"role": "assistant", "content": "response"},
        ]
        self.assistant.clear_history()
        self.assertEqual(len(self.assistant.conversation_history), 0)

    def test_build_system_prompt_without_context(self):
        prompt = self.assistant._build_system_prompt()
        self.assertIsInstance(prompt, str)
        self.assertIn("luxury travel expert", prompt)

    def test_build_system_prompt_with_flight_context(self):
        flights = [{"id": "FL001", "airline": "United", "cpp": 5.29}]
        prompt = self.assistant._build_system_prompt(flight_context=flights)
        self.assertIsInstance(prompt, str)
        self.assertIn("United", prompt)

    def test_chat_without_api_key(self):
        if not self.assistant.client:
            response = self.assistant.chat("What's a good deal?")
            self.assertIn("API key not configured", response)


if __name__ == "__main__":
    unittest.main()
