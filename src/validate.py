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
