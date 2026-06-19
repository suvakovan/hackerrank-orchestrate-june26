import pandas as pd
import os
import sys

# Add root to python path to import config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "code"))

from config import OUTPUT_CSV, SAMPLE_CLAIMS_CSV

def evaluate():
    if not os.path.exists(OUTPUT_CSV):
        print(f"Error: {OUTPUT_CSV} not found. Run main.py first.")
        return
        
    pred_df = pd.read_csv(OUTPUT_CSV)
    truth_df = pd.read_csv(SAMPLE_CLAIMS_CSV)
    
    # We only evaluate on user_ids present in sample_claims.csv
    # sample_claims has the expected ground truth
    merged = pd.merge(truth_df, pred_df, on='user_id', suffixes=('_true', '_pred'))
    
    total = len(merged)
    print(f"Evaluating {total} overlapping claims...\n")
    
    fields_to_evaluate = [
        'evidence_standard_met',
        'issue_type',
        'object_part',
        'claim_status',
        'severity'
    ]
    
    for field in fields_to_evaluate:
        true_col = f'{field}_true'
        pred_col = f'{field}_pred'
        
        # Convert to string to avoid boolean vs string mismatch
        merged[true_col] = merged[true_col].astype(str).str.lower()
        merged[pred_col] = merged[pred_col].astype(str).str.lower()
        
        correct = (merged[true_col] == merged[pred_col]).sum()
        accuracy = correct / total if total > 0 else 0
        
        print(f"--- {field.upper()} ---")
        print(f"Accuracy: {accuracy:.2%} ({correct}/{total})")
        
        # Print errors for debugging
        errors = merged[merged[true_col] != merged[pred_col]]
        if not errors.empty:
            print("Mismatches (user_id: True vs Pred):")
            for _, row in errors.iterrows():
                print(f"  {row['user_id']}: {row[true_col]} vs {row[pred_col]}")
        print()
        
if __name__ == "__main__":
    evaluate()
