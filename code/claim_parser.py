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
    Returns dict with: issue_type, object_part, claim_object
    """
    start_time = time.time()
    prompt = CLAIM_EXTRACTION_PROMPT.format(conversation=conversation)

    if USE_MOCK:
        time.sleep(0.05)

        # 1. Check mock db (sample_claims ground truth)
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

        # 2. Fallback: Rule-based heuristic extraction
        text_lower = conversation.lower()

        # --- Determine issue_type ---
        if "shatter" in text_lower or ("crack" in text_lower and ("screen" in text_lower or "windshield" in text_lower or "glass" in text_lower)):
            issue_type = "crack"
        elif "dent" in text_lower:
            issue_type = "dent"
        elif "scratch" in text_lower or "scrape" in text_lower or "mark" in text_lower:
            issue_type = "scratch"
        elif "crack" in text_lower:
            issue_type = "crack"
        elif "broke" in text_lower or "broken" in text_lower or "missing" in text_lower or "toot" in text_lower:
            issue_type = "broken_part"
        elif "stain" in text_lower or "spill" in text_lower or "coffee" in text_lower or "oily" in text_lower or "oil" in text_lower:
            issue_type = "stain"
        elif "water" in text_lower or "wet" in text_lower:
            issue_type = "water_damage"
        elif "crush" in text_lower or "crushed" in text_lower:
            issue_type = "crushed_packaging"
        elif "torn" in text_lower or "tear" in text_lower or ("open" in text_lower and claim_object == "package"):
            issue_type = "torn_packaging"
        elif "liquid" in text_lower:
            issue_type = "water_damage"
        elif "hail" in text_lower:
            issue_type = "dent"
        elif "key" in text_lower and ("missing" in text_lower or "came off" in text_lower or "faltan" in text_lower):
            issue_type = "missing_part"
        else:
            issue_type = "unknown"

        # --- Determine object_part ---
        if claim_object == "car":
            if "bumper" in text_lower:
                if "rear" in text_lower or "back" in text_lower or "behind" in text_lower or "atras" in text_lower or "trasero" in text_lower:
                    object_part = "rear_bumper"
                else:
                    object_part = "front_bumper"
            elif "windshield" in text_lower or "front glass" in text_lower:
                object_part = "windshield"
            elif "door" in text_lower:
                object_part = "door"
            elif "mirror" in text_lower:
                object_part = "side_mirror"
            elif "headlight" in text_lower or "head light" in text_lower:
                object_part = "headlight"
            elif "taillight" in text_lower or "tail light" in text_lower or "back light" in text_lower:
                object_part = "taillight"
            elif "hood" in text_lower:
                object_part = "hood"
            elif "fender" in text_lower:
                object_part = "fender"
            elif "body" in text_lower or "panel" in text_lower:
                object_part = "body"
            else:
                object_part = "unknown"
        elif claim_object == "laptop":
            if "screen" in text_lower or "display" in text_lower or "pantalla" in text_lower:
                object_part = "screen"
            elif "keyboard" in text_lower or "key" in text_lower or "tecla" in text_lower:
                object_part = "keyboard"
            elif "trackpad" in text_lower or "palm-rest" in text_lower:
                object_part = "trackpad"
            elif "hinge" in text_lower:
                object_part = "hinge"
            elif "lid" in text_lower:
                object_part = "lid"
            elif "corner" in text_lower:
                object_part = "corner"
            elif "body" in text_lower or "outer body" in text_lower:
                object_part = "body"
            elif "port" in text_lower:
                object_part = "port"
            elif "base" in text_lower:
                object_part = "base"
            else:
                object_part = "unknown"
        elif claim_object == "package":
            if "corner" in text_lower:
                object_part = "package_corner"
            elif "seal" in text_lower or "tape" in text_lower:
                object_part = "seal"
            elif "label" in text_lower:
                object_part = "label"
            elif "content" in text_lower or "item" in text_lower or "missing" in text_lower or "inside" in text_lower or "product" in text_lower:
                object_part = "contents"
            elif "side" in text_lower:
                object_part = "package_side"
            elif "box" in text_lower:
                object_part = "box"
            else:
                object_part = "unknown"
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
        raise NotImplementedError("Real API call not implemented — set GEMINI_API_KEY or OPENAI_API_KEY")
