import time
import json
import re
from utils import log_llm_call
from config import USE_MOCK
from prompts import CLAIM_EXTRACTION_PROMPT

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
        text_lower = conversation.lower()
        
        # Heuristics for damage type
        if "dent" in text_lower:
            issue_type = "dent"
        elif "scratch" in text_lower or "scrape" in text_lower:
            issue_type = "scratch"
        elif "crack" in text_lower or "shatter" in text_lower:
            issue_type = "crack"
        elif "broke" in text_lower or "missing" in text_lower:
            issue_type = "broken_part"
        elif "stain" in text_lower or "spill" in text_lower:
            issue_type = "stain"
        elif "water" in text_lower or "wet" in text_lower:
            issue_type = "water_damage"
        elif "crush" in text_lower:
            issue_type = "crushed_packaging"
        elif "torn" in text_lower or "open" in text_lower:
            issue_type = "torn_packaging"
        else:
            issue_type = "unknown"
            
        # Heuristics for object part
        if "bumper" in text_lower:
            if "rear" in text_lower or "back" in text_lower:
                object_part = "rear_bumper"
            else:
                object_part = "front_bumper"
        elif "windshield" in text_lower or "glass" in text_lower:
            object_part = "windshield"
        elif "door" in text_lower:
            object_part = "door"
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
