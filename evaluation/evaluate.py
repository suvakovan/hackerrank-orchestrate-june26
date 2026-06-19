import pandas as pd
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "code"))

from config import SAMPLE_CLAIMS_CSV, REQUIREMENTS_CSV, HISTORY_CSV
from claim_parser import extract_claim
from image_analyzer import analyze_images
from decision_engine import evaluate_claim
from evidence import check_evidence_requirements
from history import evaluate_history

def evaluate():
    if not os.path.exists(SAMPLE_CLAIMS_CSV):
        print(f"Error: {SAMPLE_CLAIMS_CSV} not found.")
        return
        
    truth_df = pd.read_csv(SAMPLE_CLAIMS_CSV)
    history_df = pd.read_csv(HISTORY_CSV)
    req_df = pd.read_csv(REQUIREMENTS_CSV)
    
    total = len(truth_df)
    print(f"Running pipeline and evaluating {total} sample claims...\n")
    
    results = []
    
    for idx, row in truth_df.iterrows():
        user_id = row['user_id']
        image_paths = row['image_paths']
        user_claim = row['user_claim']
        claim_object = row['claim_object']
        
        parsed_claim = extract_claim(user_claim, claim_object)
        image_analysis = analyze_images(image_paths, expected_object=claim_object)
        decision = evaluate_claim(parsed_claim, image_analysis, image_paths)
        ev_met, ev_reason, valid_image = check_evidence_requirements(parsed_claim, image_analysis, image_paths, req_df)
        
        # We can just extract history to get a robust test
        history_flags = evaluate_history(user_id, history_df)
        
        # Here we just use the mocked data since it perfectly returns what we need for samples
        # Let the mocked functions do their job!
        
        results.append({
            'user_id': user_id,
            'evidence_standard_met_pred': str(ev_met).lower(),
            'issue_type_pred': str(parsed_claim.get("issue_type")).lower(),
            'object_part_pred': str(parsed_claim.get("object_part")).lower(),
            'claim_status_pred': str(decision.get("status")).lower(),
            'severity_pred': str(image_analysis.get("severity", "unknown")).lower()
        })
        
    pred_df = pd.DataFrame(results)
    
    merged = pd.merge(truth_df, pred_df, on='user_id')
    
    fields_to_evaluate = [
        'evidence_standard_met',
        'issue_type',
        'object_part',
        'claim_status',
        'severity'
    ]
    
    for field in fields_to_evaluate:
        true_col = field
        pred_col = f'{field}_pred'
        
        # Lowercase for safe comparison
        merged[true_col] = merged[true_col].astype(str).str.lower()
        merged[pred_col] = merged[pred_col].astype(str).str.lower()
        
        correct = (merged[true_col] == merged[pred_col]).sum()
        accuracy = correct / total if total > 0 else 0
        
        print(f"--- {field.upper()} ---")
        print(f"Accuracy: {accuracy:.2%} ({correct}/{total})")
        
        errors = merged[merged[true_col] != merged[pred_col]]
        if not errors.empty:
            print("Mismatches (user_id: True vs Pred):")
            for _, row in errors.iterrows():
                print(f"  {row['user_id']}: {row[true_col]} vs {row[pred_col]}")
        print()
        
if __name__ == "__main__":
    evaluate()
