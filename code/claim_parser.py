import time
import json
import re
from utils import log_llm_call
from config import USE_MOCK
from prompts import CLAIM_EXTRACTION_PROMPT
from mock_db import get_mock_claim

def extract_claim(conversation, claim_object):
    """
    Extracts structured claim from the conversation.
    Returns: issue_type, object_part, claim_object
    """
    start_time = time.time()
    prompt = CLAIM_EXTRACTION_PROMPT.format(conversation=conversation)
    
    if USE_MOCK:
        time.sleep(0.05)
        # Check mock db
        mock_data = get_mock_claim(conversation)
        if mock_data:
            result = {
                "issue_type": mock_data.get("issue_type", "unknown"),
                "object_part": mock_data.get("object_part", "unknown"),
                "claim_object": mock_data.get("claim_object", "unknown")
            }
            time_taken = time.time() - start_time
            log_llm_call(prompt, json.dumps(result), time_taken)
            return result

        # Fallback Heuristics
        text_lower = conversation.lower()
        issue_type = "unknown"
        object_part = "unknown"
            
        result = {
            "issue_type": issue_type,
            "object_part": object_part,
            "claim_object": claim_object
        }
        time_taken = time.time() - start_time
        log_llm_call(prompt, json.dumps(result), time_taken)
        return result
    else:
        raise NotImplementedError("Real API call not implemented")
