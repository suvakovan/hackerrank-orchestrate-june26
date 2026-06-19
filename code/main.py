import pandas as pd
import concurrent.futures
from config import CLAIMS_CSV, HISTORY_CSV, REQUIREMENTS_CSV, OUTPUT_CSV
from claim_parser import extract_claim
from image_analyzer import analyze_images
from decision_engine import evaluate_claim
from evidence import check_evidence_requirements
from history import evaluate_history

def process_claim(row, req_df, history_df):
    """Process a single claim row through the full pipeline."""
    try:
        user_id = row['user_id']
        image_paths = row['image_paths']
        user_claim = row['user_claim']
        claim_object = row['claim_object']

        # Step 1: Parse the claim from conversation text
        parsed_claim = extract_claim(user_claim, claim_object)

        # Step 2: Analyze submitted images
        image_analysis = analyze_images(image_paths, expected_object=claim_object)

        # Step 3: Compare claim vs image evidence
        decision = evaluate_claim(parsed_claim, image_analysis, image_paths)

        # Step 4: Check evidence requirements
        ev_met, ev_reason, valid_image = check_evidence_requirements(
            parsed_claim, image_analysis, image_paths, req_df
        )

        # Step 5: Evaluate user history for risk flags
        history_flags = evaluate_history(user_id, history_df)

        # Step 6: Combine risk flags (vision flags + history flags)
        vision_flags = []
        if image_analysis.get('blurry'):
            vision_flags.append('blurry_image')
        if image_analysis.get('cropped'):
            vision_flags.append('cropped_or_obstructed')
        if image_analysis.get('glare'):
            vision_flags.append('low_light_or_glare')
        if image_analysis.get('object_type') == 'different_object':
            vision_flags.append('wrong_object')
            vision_flags.append('claim_mismatch')

        all_flags = []
        if vision_flags:
            all_flags.extend(vision_flags)
        if history_flags and history_flags != "none":
            for f in history_flags.split(';'):
                f = f.strip()
                if f and f not in all_flags:
                    all_flags.append(f)

        final_flags_str = ";".join(all_flags) if all_flags else "none"

        # Build output row with all 14 required columns
        return {
            "user_id": user_id,
            "image_paths": image_paths,
            "user_claim": user_claim,
            "claim_object": claim_object,
            "evidence_standard_met": str(ev_met).lower(),
            "evidence_standard_met_reason": ev_reason,
            "risk_flags": final_flags_str,
            "issue_type": parsed_claim.get("issue_type", "unknown"),
            "object_part": parsed_claim.get("object_part", "unknown"),
            "claim_status": decision.get("status", "not_enough_information"),
            "claim_status_justification": decision.get("justification", ""),
            "supporting_image_ids": image_analysis.get("supporting_image_ids", "none"),
            "valid_image": image_analysis.get("valid_image", "true"),
            "severity": image_analysis.get("severity", "unknown")
        }

    except Exception as e:
        print(f"Error processing user {row.get('user_id', 'unknown')}: {e}")
        return {
            "user_id": row.get('user_id', "error"),
            "image_paths": row.get('image_paths', ""),
            "user_claim": row.get('user_claim', ""),
            "claim_object": row.get('claim_object', ""),
            "evidence_standard_met": "false",
            "evidence_standard_met_reason": f"Processing error: {e}",
            "risk_flags": "manual_review_required",
            "issue_type": "unknown",
            "object_part": "unknown",
            "claim_status": "not_enough_information",
            "claim_status_justification": f"Could not process claim due to error: {e}",
            "supporting_image_ids": "none",
            "valid_image": "false",
            "severity": "unknown"
        }


def main():
    print("Starting pipeline...")

    # Read all input CSVs
    claims_df = pd.read_csv(CLAIMS_CSV)
    history_df = pd.read_csv(HISTORY_CSV)
    req_df = pd.read_csv(REQUIREMENTS_CSV)

    # Process claims concurrently but preserve row order
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(process_claim, row, req_df, history_df)
            for _, row in claims_df.iterrows()
        ]
        # Collect results IN SUBMISSION ORDER (not completion order)
        output_rows = [f.result() for f in futures]

    out_df = pd.DataFrame(output_rows)

    # Enforce exact column order per problem_statement.md lines 96-111
    columns_order = [
        "user_id",
        "image_paths",
        "user_claim",
        "claim_object",
        "evidence_standard_met",
        "evidence_standard_met_reason",
        "risk_flags",
        "issue_type",
        "object_part",
        "claim_status",
        "claim_status_justification",
        "supporting_image_ids",
        "valid_image",
        "severity"
    ]
    out_df = out_df[columns_order]
    out_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Output written to {OUTPUT_CSV} ({len(out_df)} rows, {len(columns_order)} columns)")


if __name__ == "__main__":
    main()
