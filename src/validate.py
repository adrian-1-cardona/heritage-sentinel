import json
from pathlib import Path
import sys

from logic import explain, forward_chain
from report_rules import CLAUSES, DAMAGE, MATERIALS, SEVERITIES


# Check the report shape and vocabulary before creating logical facts.
def to_facts(report):
    if not isinstance(report, dict):
        raise ValueError("schema: report must be an object")
    for key in ("id", "material", "damage", "severity"):
        if key not in report:
            raise ValueError(f"schema: missing field '{key}'")
    if not isinstance(report["id"], str) or not report["id"].strip():
        raise ValueError("schema: id must be a nonempty string")
    for key, vocabulary in (("material", MATERIALS), ("severity", SEVERITIES)):
        value = report[key]
        if not isinstance(value, str):
            raise ValueError(f"schema: {key} must be a string")
        if value not in vocabulary:
            raise ValueError(f"schema: unknown {key} '{value}'")
    if not isinstance(report["damage"], list):
        raise ValueError("schema: damage must be a list")
    if any(not isinstance(item, str) for item in report["damage"]):
        raise ValueError("schema: damage entries must be strings")
    bad = [item for item in report["damage"] if item not in DAMAGE]
    if bad:
        raise ValueError(f"schema: unknown damage type(s) {bad}")
    return (
        {f"material_{report['material']}", f"severity_{report['severity']}"}
        | {f"damage_{item}" for item in report["damage"]}
    )


# Keep schema failures separate from semantic violations and their proofs.
def validate(report):
    try:
        facts = to_facts(report)
    except ValueError as error:
        return False, [str(error)], {}
    known, why = forward_chain(facts, CLAUSES)
    reasons = sorted(symbol for symbol in known if symbol.startswith("invalid:"))
    proofs = {reason: explain(reason, why) for reason in reasons}
    return not reasons, reasons, proofs


# Validate each JSON line and record every rejection without stopping the batch.
def main(path="data/reports.jsonl", out="data/rejected.log.jsonl"):
    if Path(path).resolve() == Path(out).resolve():
        raise ValueError("input and rejection log must use different paths")
    accepted, rejected = 0, 0
    with open(path, encoding="utf-8") as source, open(out, "w", encoding="utf-8") as log:
        for number, line in enumerate(source, 1):
            try:
                report = json.loads(line)
            except json.JSONDecodeError:
                report = None
                ok, reasons, proofs = False, [f"schema: invalid JSON on line {number}"], {}
            else:
                ok, reasons, proofs = validate(report)
            if ok:
                accepted += 1
            else:
                rejected += 1
                report_id = report.get("id") if isinstance(report, dict) else None
                log.write(json.dumps({
                    "id": report_id, "reasons": reasons, "proofs": proofs
                }) + "\n")
    print(f"accepted={accepted} rejected={rejected}")
    return accepted, rejected


if __name__ == "__main__":
    main(*sys.argv[1:])
