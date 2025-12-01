"""
Configuration Module for WeatherItBetter

Loads environment variables and provides configuration to the application.
Uses python-dotenv to load from .env file.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file in project root
# Use explicit path to avoid loading .env from parent directories
# override=True ensures .env file takes precedence over shell environment
_project_root = Path(__file__).parent.parent
_env_path = _project_root / '.env'
load_dotenv(dotenv_path=_env_path, override=True)


class Config:
    """Application configuration from environment variables."""

    # API Keys - REQUIRED
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

    # Google Cloud - OPTIONAL (for advanced features)
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
    GOOGLE_CLOUD_LOCATION = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
    AGENT_ENGINE_ID = os.getenv('AGENT_ENGINE_ID')

    # Application Settings
    DEFAULT_LOCATION = os.getenv('DEFAULT_LOCATION', 'New York, NY')
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    DATA_DIR = Path(os.getenv('DATA_DIR', 'data'))

    # AI Model Settings
    AI_MODEL = os.getenv('AI_MODEL', 'gemini-2.0-flash-exp')
    AGENT_TEMPERATURE = float(os.getenv('AGENT_TEMPERATURE', '0.7'))
    AGENT_MAX_TOKENS = int(os.getenv('AGENT_MAX_TOKENS', '2000'))

    # Session Settings
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '24'))
    ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'true').lower() == 'true'

    # Streamlit Settings
    STREAMLIT_SERVER_PORT = int(os.getenv('STREAMLIT_SERVER_PORT', '8501'))
    STREAMLIT_SERVER_ADDRESS = os.getenv('STREAMLIT_SERVER_ADDRESS', 'localhost')

    @classmethod
    def validate(cls) -> bool:
        """
        Validate that required configuration is present.

        Returns:
            bool: True if all required config is present, False otherwise
        """
        # Required credentials
        required = {
            'GOOGLE_API_KEY': cls.GOOGLE_API_KEY,
            'OPENWEATHER_API_KEY': cls.OPENWEATHER_API_KEY,
            'GOOGLE_CLOUD_PROJECT': cls.GOOGLE_CLOUD_PROJECT,
            'AGENT_ENGINE_ID': cls.AGENT_ENGINE_ID,
        }

        missing = [key for key, value in required.items() if not value]

        if missing:
            print("\n❌ Missing required environment variables:")
            for key in missing:
                print(f"   - {key}")
            print("\nPlease set these in your .env file.")
            print("See .env.example for template and docs/API_CREDENTIALS.md for setup instructions.\n")
            return False

        # Check for Google Calendar credentials file
        credentials_path = Path('credentials.json')
        if not credentials_path.exists():
            print("\n❌ Missing required file: credentials.json")
            print("\nGoogle Calendar integration requires OAuth credentials.")
            print("To set up:")
            print("  1. Go to https://console.cloud.google.com/")
            print("  2. Enable Google Calendar API")
            print("  3. Create OAuth 2.0 credentials (Desktop app)")
            print("  4. Download credentials.json to project root")
            print("\nSee docs/API_CREDENTIALS.md for detailed instructions.\n")
            return False

        return True

    @classmethod
    def ensure_data_directory(cls):
        """Create data directory if it doesn't exist."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
