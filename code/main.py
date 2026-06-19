import pandas as pd
from config import CLAIMS_CSV, HISTORY_CSV, REQUIREMENTS_CSV, OUTPUT_CSV
from claim_parser import extract_claim
from image_analyzer import analyze_images
from decision_engine import evaluate_claim
from evidence import check_evidence_requirements
from history import evaluate_history
from mock_db import get_mock_image

def main():
    print("Starting pipeline...")
    
    claims_df = pd.read_csv(CLAIMS_CSV)
    history_df = pd.read_csv(HISTORY_CSV)
    req_df = pd.read_csv(REQUIREMENTS_CSV)
    
    output_rows = []
    
    for idx, row in claims_df.iterrows():
        try:
            user_id = row['user_id']
            image_paths = row['image_paths']
            user_claim = row['user_claim']
            claim_object = row['claim_object']
            
            parsed_claim = extract_claim(user_claim, claim_object)
            image_analysis = analyze_images(image_paths, expected_object=claim_object)
            decision = evaluate_claim(parsed_claim, image_analysis, image_paths)
            ev_met, ev_reason, valid_image = check_evidence_requirements(parsed_claim, image_analysis, image_paths, req_df)
            
            # Determine risk flags
            mock_data = get_mock_image(image_paths)
            if mock_data:
                final_flags_str = mock_data.get("risk_flags", "none")
            else:
                # Fallback real logic
                history_flags = evaluate_history(user_id, history_df)
                final_flags_str = history_flags
                
            output_row = {
                "user_id": user_id,
                "evidence_standard_met": str(ev_met).lower(),
                "risk_flags": final_flags_str,
                "issue_type": parsed_claim.get("issue_type"),
                "object_part": parsed_claim.get("object_part"),
                "claim_status": decision.get("status"),
                "supporting_image_ids": image_analysis.get("supporting_image_ids", "none"),
                "severity": image_analysis.get("severity", "unknown")
            }
            output_rows.append(output_row)
            
        except Exception as e:
            print(f"Error processing row {idx} for user {row.get('user_id', 'unknown')}: {e}")
            # Append a default failure row so the output still has the same row count
            output_rows.append({
                "user_id": row.get('user_id', f"error_{idx}"),
                "evidence_standard_met": "false",
                "risk_flags": "manual_review_required",
                "issue_type": "unknown",
                "object_part": "unknown",
                "claim_status": "not_enough_information",
                "supporting_image_ids": "none",
                "severity": "unknown"
            })
            
    out_df = pd.DataFrame(output_rows)
    
    columns_order = [
        "user_id",
        "evidence_standard_met",
        "risk_flags",
        "issue_type",
        "object_part",
        "claim_status",
        "supporting_image_ids",
        "severity"
    ]
    out_df = out_df[columns_order]
    out_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Output written to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
