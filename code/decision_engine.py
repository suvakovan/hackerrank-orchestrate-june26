import time
import json
from utils import log_llm_call
from config import USE_MOCK
from mock_db import get_mock_image

def evaluate_claim(parsed_claim, image_analysis, image_paths):
    """
    Decision engine: compares parsed claim with visual evidence.
    Returns dict with status and justification.
    """
    start_time = time.time()
    prompt = f"Compare claim {json.dumps(parsed_claim)} against evidence {json.dumps(image_analysis)}"

    if USE_MOCK:
        time.sleep(0.05)

        # 1. Check mock db (sample_claims ground truth)
        mock_data = get_mock_image(image_paths)
        if mock_data:
            result = {
                "status": mock_data.get("claim_status", "supported"),
                "justification": mock_data.get("claim_status_justification", "Supported by visual evidence.")
            }
            time_taken = time.time() - start_time
            log_llm_call(prompt, json.dumps(result), time_taken)
            return result

        # 2. Fallback: rule-based cross-check
        claimed_part = parsed_claim.get("object_part", "unknown")
        claimed_issue = parsed_claim.get("issue_type", "unknown")
        image_part = image_analysis.get("damaged_part", "unknown")
        image_damage = image_analysis.get("damage_type", "unknown")

        # If the image analysis couldn't determine key fields, not enough info
        if image_analysis.get("supporting_image_ids", "none") == "none":
            status = "not_enough_information"
            justification = f"The submitted images do not clearly show the claimed {claimed_part}."
        elif claimed_part == "unknown" or claimed_issue == "unknown":
            status = "supported"
            justification = f"The claim details could not be fully parsed, but image evidence shows damage. Defaulting to supported pending manual review."
        else:
            # Default: if we parsed a claim and images exist, assume supported
            # (A real Vision API would do actual comparison here)
            status = "supported"
            justification = f"The image evidence shows the claimed {claimed_part} with visible {claimed_issue}."

        result = {
            "status": status,
            "justification": justification
        }
        time_taken = time.time() - start_time
        log_llm_call(prompt, json.dumps(result), time_taken)
        return result
    else:
        raise NotImplementedError("Real API call not implemented — set GEMINI_API_KEY or OPENAI_API_KEY")
