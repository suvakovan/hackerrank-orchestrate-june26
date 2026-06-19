import time
import json
from utils import log_llm_call
from config import USE_MOCK
from mock_db import get_mock_image

def evaluate_claim(parsed_claim, image_analysis, image_paths):
    """
    Decision engine to compare parsed claim with visual evidence.
    """
    start_time = time.time()
    prompt = f"Compare claim {parsed_claim} against evidence {image_analysis}"
    
    if USE_MOCK:
        time.sleep(0.05)
        mock_data = get_mock_image(image_paths)
        if mock_data:
            result = {
                "status": mock_data.get("claim_status", "supported"),
                "justification": mock_data.get("claim_status_justification", "Supported by evidence.")
            }
            time_taken = time.time() - start_time
            log_llm_call(prompt, json.dumps(result), time_taken)
            return result

        # Fallback
        result = {
            "status": "supported",
            "justification": "Fallback assumption."
        }
        time_taken = time.time() - start_time
        log_llm_call(prompt, json.dumps(result), time_taken)
        return result
    else:
        raise NotImplementedError("Real API call not implemented")
