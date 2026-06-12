import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration loader."""
    
    BASE_DIR = Path(__file__).resolve().parent
    
    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-12345")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = FLASK_ENV == "development"
    PORT = int(os.getenv("PORT", 5000))
    
    # Directory paths
    MEMORY_DIR = BASE_DIR / "memory"
    MEMORY_FILE = MEMORY_DIR / "analysis_history.json"
    EXPORTS_DIR = BASE_DIR / "exports"
    CHARTS_DIR = BASE_DIR / "charts"
    
    @classmethod
    def init_app(cls):
        """Ensure necessary directories exist on startup."""
        cls.MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        cls.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.CHARTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.BASE_DIR.joinpath("static", "images").mkdir(parents=True, exist_ok=True)
        cls.BASE_DIR.joinpath("static", "css").mkdir(parents=True, exist_ok=True)
        cls.BASE_DIR.joinpath("static", "js").mkdir(parents=True, exist_ok=True)
        cls.BASE_DIR.joinpath("templates").mkdir(parents=True, exist_ok=True)
        
        # Initialize memory file if it does not exist
        if not cls.MEMORY_FILE.exists():
            with open(cls.MEMORY_FILE, "w", encoding="utf-8") as f:
                f.write("[]")
