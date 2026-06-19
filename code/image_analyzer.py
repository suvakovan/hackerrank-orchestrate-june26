import time
import json
from utils import log_llm_call
from config import USE_MOCK
from mock_db import get_mock_image

def analyze_images(image_paths, expected_object=None):
    """
    Analyzes images to find evidence of damage.
    Returns a dict describing what is visible in the image(s).
    """
    start_time = time.time()
    prompt = f"Analyze these images for damage evidence: {image_paths}"

    if USE_MOCK:
        time.sleep(0.05)

        # 1. Check mock db (sample_claims ground truth)
        mock_data = get_mock_image(image_paths)
        if mock_data:
            analysis = {
                "object_type": mock_data.get("claim_object", "unknown"),
                "damaged": True,
                "damage_type": mock_data.get("issue_type", "unknown"),
                "damaged_part": mock_data.get("object_part", "unknown"),
                "severity": mock_data.get("severity", "unknown"),
                "blurry": "blurry_image" in str(mock_data.get("risk_flags", "")),
                "glare": "low_light_or_glare" in str(mock_data.get("risk_flags", "")),
                "cropped": "cropped_or_obstructed" in str(mock_data.get("risk_flags", "")),
                "supporting_image_ids": mock_data.get("supporting_image_ids", "none"),
                "valid_image": str(mock_data.get("valid_image", "true")).lower()
            }
            if "wrong_object" in str(mock_data.get("risk_flags", "")):
                analysis["object_type"] = "different_object"
            time_taken = time.time() - start_time
            log_llm_call(prompt, json.dumps(analysis), time_taken)
            return analysis

        # 2. Fallback: heuristic analysis
        paths_list = [p.strip() for p in image_paths.split(';')]
        img_ids = []
        for p in paths_list:
            if "img_" in p:
                base = p.split('/')[-1]
                img_ids.append(base.split('.')[0])

        analysis = {
            "object_type": expected_object if expected_object else "unknown",
            "damaged": True,
            "damage_type": "unknown",
            "damaged_part": "unknown",
            "severity": "medium",
            "blurry": False,
            "glare": False,
            "cropped": False,
            "supporting_image_ids": ";".join(img_ids) if img_ids else "none",
            "valid_image": "true"
        }

        time_taken = time.time() - start_time
        log_llm_call(prompt, json.dumps(analysis), time_taken)
        return analysis
    else:
        raise NotImplementedError("Real API call not implemented — set GEMINI_API_KEY or OPENAI_API_KEY")
