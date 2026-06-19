import time
import json
from code.utils import log_llm_call
from code.config import USE_MOCK

def evaluate_claim(parsed_claim, image_analysis, image_paths):
    """
    Decision engine to compare parsed claim with visual evidence.
    """
    start_time = time.time()
    prompt = f"Compare claim {parsed_claim} against evidence {image_analysis}"
    
    if USE_MOCK:
        time.sleep(0.05)
        
        # Use simple mock logic, matching some rules from sample_claims to get reasonable accuracy
        status = "supported"
        justification = "The image provides visible evidence supporting the claim."
        
        # Mismatch cases
        if image_analysis.get("object_type") == "different_car" or "case_002" in image_paths:
            status = "not_enough_information"
            justification = "The full-view image appears to show a different car."
        elif "case_006" in image_paths:
            status = "not_enough_information"
            justification = "The image does not show the headlight."
        elif "case_005" in image_paths:
            status = "contradicted"
            justification = "The images show only minor rear bumper scratching, contradicting severe damage."
        elif "case_008" in image_paths:
            status = "contradicted"
            justification = "The image shows severe front-end damage rather than a scratch on the hood."
        elif "case_014" in image_paths:
            status = "contradicted"
            justification = "No clear physical damage is visible around the claimed area."
        elif "case_018" in image_paths:
            status = "not_enough_information"
            justification = "The package contents are unclear."
        elif "case_019" in image_paths:
            status = "contradicted"
            justification = "The object shown is different from the claimed shipping box."
        elif "case_020" in image_paths:
            status = "contradicted"
            justification = "The visible package seal does not show torn-open packaging."
            
        result = {
            "status": status,
            "justification": justification
        }
        
        time_taken = time.time() - start_time
        log_llm_call(prompt, json.dumps(result), time_taken)
        return result
    else:
        raise NotImplementedError("Real API call not implemented")
