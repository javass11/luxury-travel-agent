import json
from typing import Dict, List, Optional
from anthropic import Anthropic
from .config import Config
from .database import LuxuryTravelDB


class LuxuryTravelAssistant:
    def __init__(self, db: LuxuryTravelDB):
        self.db = db
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY) if Config.ANTHROPIC_API_KEY else None
        self.conversation_history = []

    def chat(
        self,
        user_message: str,
        user_id: Optional[str] = None,
        flight_context: Optional[List[Dict]] = None,
        hotel_context: Optional[List[Dict]] = None,
    ) -> str:
        if not self.client:
            return "Error: Anthropic API key not configured. Please set ANTHROPIC_API_KEY environment variable."

        system_prompt = self._build_system_prompt(user_id, flight_context, hotel_context)

        self.conversation_history.append({"role": "user", "content": user_message})

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_prompt,
            messages=self.conversation_history,
        )

        assistant_message = response.content[0].text
        self.conversation_history.append({"role": "assistant", "content": assistant_message})

        return assistant_message

    def _build_system_prompt(
        self,
        user_id: Optional[str] = None,
        flight_context: Optional[List[Dict]] = None,
        hotel_context: Optional[List[Dict]] = None,
    ) -> str:
        prompt = """You are a luxury travel expert assistant specializing in flight and hotel deals.
You help users find the best value redemptions for their miles and points.

Key responsibilities:
- Analyze cash prices vs. redemption values (cents-per-point)
- Identify sweet spots and outsized-value redemptions
- Consider loyalty program benefits and elite status
- Provide personalized recommendations based on user preferences
- Highlight suite upgrades and elite night credits
"""

        if user_id:
            loyalty_profile = self.db.get_loyalty_profile(user_id)
            if loyalty_profile:
                prompt += f"\n\nUser's Loyalty Profile:\n{json.dumps(loyalty_profile, indent=2)}"

        if flight_context:
            prompt += f"\n\nAvailable Flights:\n{json.dumps(flight_context[:3], indent=2)}"

        if hotel_context:
            prompt += f"\n\nAvailable Hotels:\n{json.dumps(hotel_context[:3], indent=2)}"

        return prompt

    def clear_history(self):
        self.conversation_history = []
