import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")

    AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
    AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
    DUFFEL_ACCESS_TOKEN = os.getenv("DUFFEL_ACCESS_TOKEN")
    SEATS_AERO_API_KEY = os.getenv("SEATS_AERO_API_KEY")

    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///luxury_travel.db")

    @classmethod
    def validate_api_credentials(cls):
        missing = []
        required_apis = {
            "AMADEUS_CLIENT_ID": cls.AMADEUS_CLIENT_ID,
            "AMADEUS_CLIENT_SECRET": cls.AMADEUS_CLIENT_SECRET,
            "DUFFEL_ACCESS_TOKEN": cls.DUFFEL_ACCESS_TOKEN,
            "SEATS_AERO_API_KEY": cls.SEATS_AERO_API_KEY,
            "ANTHROPIC_API_KEY": cls.ANTHROPIC_API_KEY,
        }
        for key, value in required_apis.items():
            if not value:
                missing.append(key)
        return missing
