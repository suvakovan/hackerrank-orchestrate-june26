import logging
import time
import json
from config import LOG_FILE

# Set up logging to append to log.txt
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_llm_call(prompt, response, time_taken, error=None):
    """
    Log every LLM/VLM call as required by the challenge.
    """
    log_entry = {
        "prompt_sent": prompt,
        "response_received": response,
        "time_taken_seconds": round(time_taken, 2),
        "error": error
    }
    
    # Write to log in a structured way
    logging.info(f"LLM_CALL: {json.dumps(log_entry)}")
    
    # If there's an error, also log it as an error
    if error:
        logging.error(f"LLM_ERROR: {error}")

def mock_llm_call(prompt_type, reference_data=None):
    """
    Simulates a slight delay for LLM calls if in mock mode.
    """
    time.sleep(0.1) # Simulate network latency
    pass
