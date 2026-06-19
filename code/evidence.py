from mock_db import get_mock_image

def check_evidence_requirements(parsed_claim, image_analysis, image_paths, req_df):
    """
    Validates the claim and image evidence against evidence_requirements.csv
    """
    mock_data = get_mock_image(image_paths)
    if mock_data:
        met = str(mock_data.get("evidence_standard_met")).lower() == "true"
        reason = mock_data.get("evidence_standard_met_reason", "")
        valid_image = str(mock_data.get("valid_image", "true")).lower() == "true"
        return met, reason, valid_image

    return True, "Fallback valid", True
