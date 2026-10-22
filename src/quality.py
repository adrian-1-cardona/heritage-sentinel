import json, sys
from collections import Counter
from validate import validate
from report_model import ReportModel, calibrate
from prob import chi_square

# Chi-square critical values at p = 0.001: df 4 for five materials, df 2 for three severities.
CHI2_CRIT_001 = {2: 13.816, 4: 18.467}

def load(path):
    with open(path) as f:
        return [json.loads(l) for l in f]

def classify(report, model, threshold):
    """Gate 1: schema + logic (Lab 4). Gate 2: statistical plausibility.
    Returns (verdict, detail) where verdict is accept / quarantine / reject."""
    ok, reasons, _ = validate(report)
    if not ok:
        return "reject", reasons
    likelihood = model.log_likelihood(report)
    if likelihood < threshold:
        return "quarantine", [
            f"improbable: log-likelihood {likelihood:.2f} < threshold {threshold:.2f}"
        ]
    return "accept", []

# One batch can drift in what it is made of, in how bad it is, or in either alone.
def batch_drift(reports, model):
    """Batch-level check. Returns {check_name: (statistic, critical_value, drifted)}."""
    checks = {
        "material_mix": (Counter(r["material"] for r in reports), model.p_material, 4),
        "severity_mix": (Counter(r["severity"] for r in reports), model.p_severity_mix, 2),
    }
    drift = {}
    for name, (observed, expected, df) in checks.items():
        s = chi_square(observed, expected)
        drift[name] = (round(s, 2), CHI2_CRIT_001[df], s > CHI2_CRIT_001[df])
    return drift

def run(batch_path, reference_path="data/reference.jsonl", q=0.02):
    ref = load(reference_path)
    model = ReportModel(ref)
    threshold = calibrate(model, ref, q)
    verdicts, passed, summary = {}, [], Counter()
    for r in load(batch_path):
        v, detail = classify(r, model, threshold)
        verdicts[r.get("id")] = (v, detail)
        summary[v] += 1
        if v != "reject":
            passed.append(r)
    return {"summary": dict(summary), "drift": batch_drift(passed, model),
            "verdicts": verdicts, "threshold": round(threshold, 2)}

def main(batch_path, log_path=None):
    res = run(batch_path)
    log_path = log_path or batch_path.replace(".jsonl", ".quality.log.jsonl")
    with open(log_path, "w") as log:
        for rid, (verdict, detail) in res["verdicts"].items():
            if verdict != "accept":
                log.write(json.dumps({"id": rid, "verdict": verdict, "detail": detail}) + "\n")
    print(json.dumps({k: res[k] for k in ("summary", "drift", "threshold")}))

if __name__ == "__main__":
    main(*sys.argv[1:])
