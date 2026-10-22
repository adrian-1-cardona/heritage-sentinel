import hashlib, json, os, subprocess, sys, tempfile
import pytest
import make_data
from quality import load, classify, run, batch_drift
from report_model import ReportModel, calibrate
from validate import validate

REF = load("data/reference.jsonl")
MODEL = ReportModel(REF)
THRESHOLD = calibrate(MODEL, REF, 0.02)

def by_id(path):
    return {r["id"]: r for r in load(path)}

A = by_id("data/incoming_a.jsonl")

def test_reference_data_passes_the_logic_gate():
    # Your "trusted" data must itself obey the Lab 4 rules.
    assert all(validate(r)[0] for r in REF)

def test_calibration_flags_about_two_percent_of_reference():
    flagged = sum(MODEL.log_likelihood(r) < THRESHOLD for r in REF)
    assert 7 <= flagged <= 9          # 2% of 400 = 8, allow +/-1 for percentile conventions

@pytest.mark.parametrize("rid", ["a-odd1", "a-odd2", "a-odd3"])
def test_logic_valid_but_improbable_is_quarantined(rid):
    assert validate(A[rid])[0]                       # Lab 4 alone would accept it
    verdict, detail = classify(A[rid], MODEL, THRESHOLD)
    assert verdict == "quarantine" and "improbable" in detail[0]

@pytest.mark.parametrize("rid", ["a-bad1", "a-bad2"])
def test_impossible_is_rejected_not_quarantined(rid):
    verdict, _ = classify(A[rid], MODEL, THRESHOLD)
    assert verdict == "reject"

def test_unseen_combination_scores_finite():
    ll = MODEL.log_likelihood(A["a-odd1"])           # stone + corrosion never occurs in reference
    assert ll == ll and ll > -100                    # not NaN, not -inf

def test_batch_a_summary():
    res = run("data/incoming_a.jsonl")
    assert res["summary"] == {"accept": 100, "quarantine": 3, "reject": 2}
    assert res["drift"]["material_mix"][2] is False

def test_clean_batches_rarely_raise_drift_alarms():
    alarms = sum(
        batch_drift(make_data.make_batch(s, 100, "c", make_data.MATERIAL_P), MODEL)["material_mix"][2]
        for s in range(100, 150))
    assert alarms <= 1

def test_pipeline_output_is_reproducible_across_processes():
    runs = [subprocess.run([sys.executable, "src/quality.py", "data/incoming_a.jsonl",
                            os.devnull], capture_output=True, text=True, check=True).stdout
            for _ in range(2)]
    assert runs[0] == runs[1]
