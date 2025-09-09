import json
import pytest
from app.services.fraud_service import FraudService  # adjust to your service

@pytest.mark.parametrize("case_file", ["fraud_cases.json", "legit_cases.json"])
def test_eval_cases(case_file):
    # Load cases
    with open(f"fixtures/evals/{case_file}") as f:
        cases = json.load(f)

    for case in cases:
        input_txn = case["input"]
        expected = case["expected"]

        result = FraudService.evaluate_transaction(input_txn)

        assert result["flagged"] == expected["flagged"], f"Case {case['id']} failed"
        if expected.get("reason"):
            assert result.get("reason") == expected["reason"]
