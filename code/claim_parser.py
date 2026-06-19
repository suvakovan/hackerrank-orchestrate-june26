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
        # Mocking LLM using heuristics
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
        elif "mirror" in text_lower:
            object_part = "side_mirror"
        elif "headlight" in text_lower:
            object_part = "headlight"
        elif "screen" in text_lower or "pantalla" in text_lower:
            object_part = "screen"
        elif "hinge" in text_lower:
            object_part = "hinge"
        elif "keyboard" in text_lower or "key" in text_lower or "tecla" in text_lower:
            object_part = "keyboard"
        elif "trackpad" in text_lower:
            object_part = "trackpad"
        elif "corner" in text_lower:
            if claim_object == "package":
                object_part = "package_corner"
            else:
                object_part = "corner"
        elif "seal" in text_lower:
            object_part = "seal"
        elif "label" in text_lower:
            object_part = "label"
        elif "side" in text_lower and claim_object == "package":
            object_part = "package_side"
        else:
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
        # Here you would implement real API calls
        raise NotImplementedError("Real API call not implemented in this demo")
