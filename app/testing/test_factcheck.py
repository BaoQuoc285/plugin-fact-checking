import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import json
import pytest
from app.core.factcheck import FactCheck  # fixed import to match filename

@pytest.fixture(scope="module")
def fact_checker():
    return FactCheck(
        search_api_key="297e5175d5055b5816ceb37fe503851598633097",
        model_path="C://Users//ADMIN//Desktop//IE403-PluginFactChecking//app//models//weights//model_pho_bert_base.pth",
        llm_api_params={"provider": "GEMINI", "model_name": "gemini-2.0-flash", "api_key": "AIzaSyCe78RhtA-88OgTPRXDCBCR4gP3XwX6w-Y"},
        selector_method=None
    )

def load_test_data(json_path):
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)

@pytest.mark.parametrize("claim,label", [
    (item["claim"], item["label"]) for item in load_test_data(r"C:\Users\ADMIN\Desktop\IE403-PluginFactChecking\app\testing\test.json")
])
def test_factcheck_label(fact_checker, claim, label):
    result = fact_checker.check(claim, num_evidence=5, top_k=3)
    # Giả sử result['evidences'][0]['label'] là nhãn dự đoán
    predicted = result["accuracy_percent"]
    predicted_label = "supported" if predicted >= 50 else "refuted"
    ground_label = "supported" if label == "0" else "refuted"
    assert predicted_label == ground_label, f"Claim: {claim}, Predicted: {predicted_label}, Ground Truth: {ground_label}"