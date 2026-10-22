import json
from pathlib import Path
import random
import re

import pytest

from logic import explain, forward_chain
from report_rules import CLAUSES, DAMAGE, MATERIALS, SEVERITIES
from validate import to_facts, validate
import validate as validation


REPORTS = {
    report["id"]: report
    for report in map(
        json.loads,
        (Path(__file__).resolve().parents[1] / "data/reports.jsonl").read_text().splitlines(),
    )
}


# Invalid vocabulary and missing fields must fail before inference.
@pytest.mark.parametrize(
    "rid,fragment", [("r10", "missing field"), ("r11", "unknown material")]
)
def test_schema_errors_are_not_logic_errors(rid, fragment):
    ok, reasons, proofs = validate(REPORTS[rid])
    assert not ok
    assert reasons[0].startswith("schema:") and fragment in reasons[0]
    assert proofs == {}


# Malformed JSON values produce schema errors instead of runtime exceptions.
@pytest.mark.parametrize(
    "report",
    [None, [], "report", {}, *[
        {**REPORTS["r1"], key: value}
        for key, value in [
            ("id", ""), ("id", 1), ("material", []), ("severity", {}),
            ("severity", "unknown"), ("damage", "crack"), ("damage", None),
            ("damage", [{}]), ("damage", ["unknown"]),
        ]
    ]],
)
def test_malformed_reports_are_schema_errors(report):
    ok, reasons, proofs = validate(report)
    assert not ok and reasons[0].startswith("schema:") and proofs == {}
    with pytest.raises(ValueError, match="schema:"):
        to_facts(report)


# Reverse rule order forces the engine to make more than one pass.
def test_chain_derives_transitively():
    known, why = forward_chain(
        {"a"}, [(frozenset({"b"}), "c"), (frozenset({"a"}), "b")]
    )
    assert known == {"a", "b", "c"}
    assert why == {"a": None, "b": frozenset({"a"}), "c": frozenset({"b"})}


# Cycles cannot add a conclusion that is already known.
def test_cycle_terminates():
    known, why = forward_chain(
        {"a"}, [(frozenset({"a"}), "b"), (frozenset({"b"}), "a")]
    )
    assert known == {"a", "b"}
    assert why["a"] is None
    assert explain("b", why) == ["b  because:", "  a  (given)"]


# Empty premises fire unconditionally; unsupported cycles derive nothing.
def test_empty_premises_and_unseeded_cycle():
    assert forward_chain([], [(frozenset(), "a")]) == (
        {"a"}, {"a": frozenset()}
    )
    assert forward_chain(
        [], [(frozenset({"a"}), "b"), (frozenset({"b"}), "a")]
    ) == (set(), {})


# Rule iterators remain available on every inference pass.
def test_clause_iterator():
    clauses = iter([(frozenset({"b"}), "c"), (frozenset({"a"}), "b")])
    assert forward_chain({"a"}, clauses)[0] == {"a", "b", "c"}


# Every clause must fire with all premises and require each individual premise.
@pytest.mark.parametrize("clause", CLAUSES, ids=lambda clause: str(clause))
def test_every_clause_fires(clause):
    premises, conclusion = clause
    known, why = forward_chain(premises, [clause])
    assert conclusion in known and why[conclusion] == premises
    for premise in premises:
        assert conclusion not in forward_chain(premises - {premise}, [clause])[0]


# Accepted reports should have neither reasons nor rejection proofs.
@pytest.mark.parametrize("rid", ["r1", "r3", "r5", "r7"])
def test_valid_reports_accepted(rid):
    assert validate(REPORTS[rid]) == (True, [], {})


# Each starter constraint has a report that triggers it in isolation.
@pytest.mark.parametrize("rid,reason", [
    ("r2", "invalid:structural_risk_marked_minor"),
    ("r4", "invalid:rot_on_inorganic"),
    ("r6", "invalid:corrosion_on_organic"),
    ("r8", "invalid:none_but_damaged"),
])
def test_each_rule_fires_alone(rid, reason):
    ok, reasons, proofs = validate(REPORTS[rid])
    assert not ok and reasons == [reason]
    assert set(proofs) == {reason}


# A report can violate more than one constraint without hiding either failure.
def test_multiple_violations_all_reported():
    ok, reasons, proofs = validate(REPORTS["r9"])
    assert not ok
    assert reasons == [
        "invalid:rot_on_inorganic", "invalid:structural_risk_marked_minor"
    ]
    assert list(proofs) == reasons


# Rejection proofs must match the expected derivation and end in given facts.
def test_proofs_bottom_out_in_given_facts():
    reason = "invalid:structural_risk_marked_minor"
    lines = validate(REPORTS["r2"])[2][reason]
    assert lines == [
        f"{reason}  because:",
        "  severity_minor  (given)",
        "  structural_risk  because:",
        "    damage_crack  (given)",
        "    damage_loose_base  (given)",
    ]
    leaves = [line for line in lines if "because" not in line]
    assert leaves and all("(given)" in line for line in leaves)


# Shuffling clauses must preserve conclusions, even for multiple violations.
def test_clause_order_irrelevant():
    facts = to_facts(REPORTS["r9"])
    expected, _ = forward_chain(facts, CLAUSES)
    for seed in range(20):
        shuffled = CLAUSES[:]
        random.Random(seed).shuffle(shuffled)
        assert forward_chain(facts, shuffled)[0] == expected


# Removing a constraint changes the result; restoring it must restore rejection.
def test_deleting_a_rule_is_caught():
    original = validation.CLAUSES
    try:
        validation.CLAUSES = [
            clause for clause in original if clause[1] != "invalid:rot_on_inorganic"
        ]
        assert validate(REPORTS["r4"]) == (True, [], {})
    finally:
        validation.CLAUSES = original
    assert validate(REPORTS["r4"])[1] == ["invalid:rot_on_inorganic"]


# First-fired proofs can differ when alternative rules derive the same goal.
def test_alternative_proofs_depend_on_clause_order():
    clauses = [(frozenset({"a"}), "goal"), (frozenset({"b"}), "goal")]
    known, why = forward_chain({"a", "b"}, clauses)
    reversed_known, reversed_why = forward_chain({"a", "b"}, clauses[::-1])
    assert known == reversed_known
    assert why["goal"] != reversed_why["goal"]
    assert explain("goal", why) == ["goal  because:", "  a  (given)"]
    assert explain("goal", reversed_why) == ["goal  because:", "  b  (given)"]


# Corroded ceramic and cracked textile are rare, not impossible, so no rule may reject them.
@pytest.mark.parametrize("rid", ["r12", "r13"])
def test_retired_rarity_rules_accept_their_old_targets(rid):
    assert validate(REPORTS[rid]) == (True, [], {})


# A hard constraint may never contradict the trusted reference data it is checked against.
def test_no_rule_rejects_the_reference_data():
    reference = (Path(__file__).resolve().parents[1] / "data/reference.jsonl").read_text()
    assert all(validate(json.loads(line))[0] for line in reference.splitlines())


# Domain vocabulary belongs to the knowledge base, never a reusable engine.
@pytest.mark.parametrize("module", ["src/logic.py", "src/prob.py"])
def test_generic_modules_have_no_heritage_vocabulary(module):
    source = (Path(__file__).resolve().parents[1] / module).read_text()
    words = set(re.findall(r"[A-Za-z]+", source))
    assert not words & (MATERIALS | DAMAGE | SEVERITIES)


# Generated witnesses expose the removal of every integrity constraint.
@pytest.mark.parametrize("goal", sorted({
    goal for _, goal in CLAUSES if goal.startswith("invalid:")
}))
def test_generated_witness_catches_each_deleted_constraint(goal, monkeypatch):
    from generate_reports import generate_reports

    report = generate_reports()[goal]
    assert goal in validate(report)[1]
    monkeypatch.setattr(validation, "CLAUSES", [clause for clause in CLAUSES if clause[1] != goal])
    assert goal not in validate(report)[1]
