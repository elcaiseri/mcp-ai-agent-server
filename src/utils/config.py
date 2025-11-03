"""Configuration and environment management."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    
    # Server Configuration
    SERVER_NAME = os.getenv("MCP_SERVER_NAME", "ai-agent-server")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "CRITICAL")
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", 3001))
    
    # Directories
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "WORKSPACE"
    TEMP_DIR = BASE_DIR / "TEMP"

    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5")
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.TEMP_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def validate(cls):
        """Validate configuration."""
        if not cls.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set. AI agent features will be limited.")
        return True

config = Config()
