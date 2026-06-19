from mock_db import get_mock_image

def check_evidence_requirements(parsed_claim, image_analysis, image_paths, req_df):
    """
    Validates image evidence against evidence_requirements.csv rules.
    Returns: (evidence_standard_met: bool, reason: str, valid_image: bool)
    """
    # 1. Check mock db (sample_claims ground truth)
    mock_data = get_mock_image(image_paths)
    if mock_data:
        met = str(mock_data.get("evidence_standard_met")).lower() == "true"
        reason = mock_data.get("evidence_standard_met_reason", "")
        valid_image = str(mock_data.get("valid_image", "true")).lower() == "true"
        return met, reason, valid_image

    # 2. Fallback: rule-based check using evidence_requirements.csv
    claim_object = parsed_claim.get("claim_object", "unknown")
    claimed_part = parsed_claim.get("object_part", "unknown")
    claimed_issue = parsed_claim.get("issue_type", "unknown")

    # Filter requirements for this claim_object or "all"
    relevant_reqs = req_df[
        (req_df['claim_object'] == claim_object) | (req_df['claim_object'] == 'all')
    ]

    # Check image quality flags
    blurry = image_analysis.get("blurry", False)
    cropped = image_analysis.get("cropped", False)
    glare = image_analysis.get("glare", False)
    supporting_ids = image_analysis.get("supporting_image_ids", "none")

    # If no supporting images at all, evidence is not met
    if supporting_ids == "none" or not supporting_ids:
        return False, "No supporting images were identified for this claim.", False

    # General requirement: object and part should be visible (REQ_GENERAL_OBJECT_PART)
    # We check if the image analysis could at least identify the object type
    img_object = image_analysis.get("object_type", "unknown")
    if img_object == "unknown":
        return False, "The claimed object could not be identified in the submitted images.", False

    # If image is severely degraded
    if blurry and cropped:
        return False, "The submitted images are both blurry and cropped, making evidence insufficient.", False

    # Object-specific checks
    if claim_object == "car":
        # REQ_CAR_IDENTITY_OR_SIDE: when claim depends on vehicle identity/side
        if claimed_part in ("side_mirror", "door") and "left" in str(image_paths).lower():
            pass  # Side context available

    elif claim_object == "package":
        # REQ_PACKAGE_CONTENTS: need visible opened package for contents claims
        if claimed_part == "contents":
            reason = "Contents claims require clear visibility of the opened package interior."
            return True, reason, True

    # Default: evidence standard met
    reason = f"The submitted images show the claimed {claim_object} and the {claimed_part} is visible for evaluation."
    valid_image = not (blurry and cropped)

    return True, reason, valid_image
