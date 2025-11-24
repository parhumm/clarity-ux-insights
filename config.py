"""Configuration management for Clarity API integration."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
EXPORT_DIR = DATA_DIR / "exports"

# Clarity API Configuration
CLARITY_API_TOKEN = os.getenv("CLARITY_API_TOKEN")
CLARITY_PROJECT_ID = os.getenv("CLARITY_PROJECT_ID", "televika")
API_BASE_URL = os.getenv("API_BASE_URL", "https://www.clarity.ms/export-data/api/v1")

# API Endpoints
API_ENDPOINT_PROJECT_INSIGHTS = f"{API_BASE_URL}/project-live-insights"

# Database Configuration
DB_PATH = PROJECT_ROOT / os.getenv("DB_PATH", "data/clarity_data.db")

# API Rate Limiting
MAX_REQUESTS_PER_DAY = 10
MAX_DAYS_PER_REQUEST = 3

# Validate critical configuration
def validate_config():
    """Validate that all required configuration is present."""
    errors = []

    if not CLARITY_API_TOKEN:
        errors.append("CLARITY_API_TOKEN is missing from .env file")
    elif not CLARITY_API_TOKEN.startswith("eyJ"):
        errors.append("CLARITY_API_TOKEN doesn't appear to be a valid JWT token")

    if not CLARITY_PROJECT_ID:
        errors.append("CLARITY_PROJECT_ID is missing")

    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

    return True

def ensure_directories():
    """Create necessary directories if they don't exist."""
    directories = [DATA_DIR, RAW_DATA_DIR, EXPORT_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    return True

if __name__ == "__main__":
    # Test configuration
    print("Testing configuration...")
    try:
        validate_config()
        print("✓ Configuration valid")
        print(f"✓ API Token: {CLARITY_API_TOKEN[:20]}...")
        print(f"✓ Project ID: {CLARITY_PROJECT_ID}")
        print(f"✓ API Endpoint: {API_ENDPOINT_PROJECT_INSIGHTS}")

        ensure_directories()
        print(f"✓ Data directory: {DATA_DIR}")
        print(f"✓ Raw data directory: {RAW_DATA_DIR}")
        print(f"✓ Export directory: {EXPORT_DIR}")

        print("\n✅ All configuration tests passed!")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        exit(1)
