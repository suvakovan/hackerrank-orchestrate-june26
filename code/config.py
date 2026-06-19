import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")

# Dataset files
CLAIMS_CSV = os.path.join(DATASET_DIR, "claims.csv")
SAMPLE_CLAIMS_CSV = os.path.join(DATASET_DIR, "sample_claims.csv")
HISTORY_CSV = os.path.join(DATASET_DIR, "user_history.csv")
REQUIREMENTS_CSV = os.path.join(DATASET_DIR, "evidence_requirements.csv")

# Output files
OUTPUT_CSV = os.path.join(BASE_DIR, "output.csv")
LOG_FILE = os.path.join(BASE_DIR, "log.txt")

# API Keys and settings
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Fallback mode (If no key is provided, the mock engine will read from sample_claims to simulate responses)
USE_MOCK = not bool(GEMINI_API_KEY or OPENAI_API_KEY)
