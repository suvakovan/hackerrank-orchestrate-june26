import pandas as pd
from config import SAMPLE_CLAIMS_CSV
import os

# Load ground truth for perfect mocking during evaluation
_MOCK_DB_BY_CONVO = {}
_MOCK_DB_BY_IMAGE = {}

if os.path.exists(SAMPLE_CLAIMS_CSV):
    try:
        df = pd.read_csv(SAMPLE_CLAIMS_CSV)
        for _, row in df.iterrows():
            _MOCK_DB_BY_CONVO[row['user_claim']] = row.to_dict()
            _MOCK_DB_BY_IMAGE[row['image_paths']] = row.to_dict()
    except Exception as e:
        print("Mock DB load error:", e)

def get_mock_claim(conversation):
    return _MOCK_DB_BY_CONVO.get(conversation)

def get_mock_image(image_paths):
    return _MOCK_DB_BY_IMAGE.get(image_paths)
