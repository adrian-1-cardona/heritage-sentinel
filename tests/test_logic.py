import json
from pathlib import Path

import pytest

from logic import explain, forward_chain
from validate import to_facts, validate


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
