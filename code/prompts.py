CLAIM_EXTRACTION_PROMPT = """
You are an expert claims processor. Given a conversation between a customer and support, extract the core claim information.

Return EXACTLY a valid JSON object with the following keys (no markdown wrapping, no extra text):
- "issue_type": The type of damage or issue (e.g., "scratch", "dent", "crack", "broken_part", "stain", "water_damage", "crushed_packaging", "torn_packaging")
- "object_part": The specific part that is damaged (e.g., "door", "front_bumper", "screen", "keyboard", "hinge", "package_corner", "seal")
- "claim_object": The main object (e.g., "car", "laptop", "package")

Conversation:
{conversation}

(Developer Note: In production, this prompt uses response_format=json_object or instructor Pydantic models to guarantee valid parsing.)
"""

IMAGE_ANALYSIS_PROMPT = """
You are an expert image analyst for insurance claims. Look at the provided image(s).

Identify the following:
- object_type: (car, laptop, package, etc.)
- damaged: true or false
- damage_type: what kind of damage is visible? (scratch, dent, crack, broken_part, etc.)
- damaged_part: what part of the object is damaged?
- blurry: true or false
- glare: true or false
- cropped: true or false
- severity: (low, medium, high, unknown)

Return EXACTLY a JSON object matching these keys.
"""

DECISION_PROMPT = """
Compare the extracted claim with the visual evidence to make a final decision.
Claim: {claim_json}
Evidence: {evidence_json}

Is the claim supported, contradicted, or is there not enough information?
Output JSON with:
- "status": ("supported", "contradicted", "not_enough_information")
- "justification": string explaining why.
"""
