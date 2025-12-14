import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for Health Compass"""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    CHROMA_DB_DIR = DATA_DIR / "chroma_db"
    
    # API Keys
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    SITE_URL = os.getenv("SITE_URL", "")
    SITE_NAME = os.getenv("SITE_NAME", "Health Compass")
    
    # Model settings
    DEFAULT_LLM_MODEL = "mistralai/mistral-7b-instruct:free"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # RAG settings
    DEFAULT_N_RESULTS = 5
    CHUNK_SIZE = 400
    CHUNK_OVERLAP = 50
    
    # LLM parameters
    DEFAULT_TEMPERATURE = 0.2
    DEFAULT_MAX_TOKENS = 1500
    
    # Scraping settings
    DEFAULT_SCRAPE_LIMIT = 50
    SCRAPE_DELAY = 1  # seconds between requests
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        if not cls.OPENROUTER_API_KEY:
            errors.append("OPENROUTER_API_KEY not set in .env file")
        
        if not cls.DATA_DIR.exists():
            cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        if errors:
            return False, errors
        
        return True, []
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("\n" + "="*60)
        print("HEALTH COMPASS CONFIGURATION")
        print("="*60)
        print(f"Project Root: {cls.PROJECT_ROOT}")
        print(f"Data Directory: {cls.DATA_DIR}")
        print(f"Vector DB: {cls.CHROMA_DB_DIR}")
        print(f"\nLLM Model: {cls.DEFAULT_LLM_MODEL}")
        print(f"Embedding Model: {cls.EMBEDDING_MODEL}")
        print(f"\nAPI Key Set: {'Yes' if cls.OPENROUTER_API_KEY else 'No'}")
        print(f"Site URL: {cls.SITE_URL}")
        print("="*60 + "\n")

if __name__ == "__main__":
    config = Config()
    config.print_config()
    
    is_valid, errors = config.validate()
    if is_valid:
        print("✅ Configuration is valid!")
    else:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"   - {error}")