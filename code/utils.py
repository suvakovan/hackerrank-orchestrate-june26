import logging
import time
import json
import hashlib
import sqlite3
import os
from config import LOG_FILE, BASE_DIR

# Set up logging to append to log.txt
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_llm_call(prompt, response, time_taken, error=None):
    """
    Log every LLM/VLM call as required by the challenge.
    Stores: prompt sent, response received, time taken, errors.
    """
    log_entry = {
        "prompt_sent": prompt[:500],  # Truncate long prompts for readability
        "response_received": response[:500],
        "time_taken_seconds": round(time_taken, 2),
        "error": error
    }

    logging.info(f"LLM_CALL: {json.dumps(log_entry)}")

    if error:
        logging.error(f"LLM_ERROR: {error}")


# =============================================================================
# PRODUCTION STUBS — Retry and Cache
# These are importable and functional, but not wired into the mock pipeline.
# In production, call_llm_with_retry() replaces the direct API call.
# =============================================================================

# --- SQLite Cache ---

CACHE_DB_PATH = os.path.join(BASE_DIR, "llm_cache.db")

def _init_cache():
    """Initialize the SQLite cache table if it doesn't exist."""
    conn = sqlite3.connect(CACHE_DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS api_cache "
        "(hash_key TEXT PRIMARY KEY, response TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    conn.commit()
    return conn

def _get_cache_key(prompt_str, image_hashes=None):
    """
    Generates a stable SHA-256 cache key from the prompt and image hashes.
    In production, image_hashes would be computed from the raw image bytes
    to detect duplicate submissions.
    """
    content = prompt_str + str(sorted(image_hashes or []))
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def get_cached_response(prompt_str, image_hashes=None):
    """
    Fetch a cached LLM response from SQLite.
    Returns the parsed JSON dict, or None if not cached.
    """
    key = _get_cache_key(prompt_str, image_hashes)
    conn = _init_cache()
    cursor = conn.cursor()
    cursor.execute("SELECT response FROM api_cache WHERE hash_key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None

def set_cached_response(prompt_str, response_dict, image_hashes=None):
    """
    Save a successful LLM response into the SQLite cache.
    """
    key = _get_cache_key(prompt_str, image_hashes)
    conn = _init_cache()
    conn.execute(
        "INSERT OR REPLACE INTO api_cache (hash_key, response) VALUES (?, ?)",
        (key, json.dumps(response_dict))
    )
    conn.commit()
    conn.close()


# --- Retry with Exponential Backoff ---
# Requires: pip install tenacity
# Uncomment the decorator when tenacity is installed.

# from tenacity import retry, stop_after_attempt, wait_exponential

# @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_llm_with_retry(prompt_str, image_paths=None, model="gpt-4o"):
    """
    Production LLM caller with cache-first strategy and retry logic.

    Flow:
    1. Check SQLite cache → return immediately if hit.
    2. Call the LLM API (with tenacity exponential backoff on failure).
    3. Cache the successful response for future calls.

    In production, enable the @retry decorator above and replace
    the placeholder API call with the actual openai/google-generativeai call.
    """
    # Compute image hashes for cache key (placeholder)
    image_hashes = [hashlib.sha256(p.encode()).hexdigest()[:16] for p in (image_paths or [])]

    # 1. Check cache
    cached = get_cached_response(prompt_str, image_hashes)
    if cached:
        return cached

    # 2. Call API (placeholder — replace with real API call)
    # response = openai.ChatCompletion.create(model=model, messages=[...])
    response_dict = {"status": "placeholder", "note": "Replace with real API call"}

    # 3. Cache result
    set_cached_response(prompt_str, response_dict, image_hashes)

    return response_dict
