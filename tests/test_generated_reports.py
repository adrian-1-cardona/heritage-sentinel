import json
from pathlib import Path
import random

import pytest

from generate_reports import generate_reports, main
from logic import backward_chain, forward_chain
from report_rules import CLAUSES, FACT_SYMBOLS, report_from_facts
from validate import to_facts, validate


GOALS = sorted({goal for _, goal in CLAUSES if goal.startswith("invalid:")})


# Every integrity constraint gets a minimal support and a rejected generated report.
@pytest.mark.parametrize("goal", GOALS)
def test_generated_report_is_minimal_and_triggers_goal(goal):
    report = generate_reports()[goal]
    assert goal in validate(report)[1]
    for damage in report["damage"]:
        near_miss = {**report, "damage": [item for item in report["damage"] if item != damage]}
        assert goal not in validate(near_miss)[1]
    for support in backward_chain(goal, CLAUSES, FACT_SYMBOLS):
        assert goal in forward_chain(support, CLAUSES)[0]
        for fact in support:
            assert goal not in forward_chain(support - {fact}, CLAUSES)[0]


# Compare logical coverage against every report written by hand.
def test_hand_written_reports_cover_every_generated_goal():
    path = Path(__file__).resolve().parents[1] / "data/reports.jsonl"
    covered = {
        reason for report in map(json.loads, path.read_text().splitlines())
        for reason in validate(report)[1] if reason.startswith("invalid:")
    }
    assert set(generate_reports()) == covered == set(GOALS)


# Rule reordering must not change which minimal reports get generated.
def test_generated_reports_are_order_independent():
    expected = generate_reports()
    for seed in range(20):
        clauses = CLAUSES[:]
        random.Random(seed).shuffle(clauses)
        assert generate_reports(clauses) == expected


# Contradictory material or severity assumptions cannot form one report.
@pytest.mark.parametrize("facts", [
    {"material_stone", "material_metal"},
    {"severity_none", "severity_major"},
    {"not_a_report_fact"},
])
def test_report_from_facts_rejects_inconsistent_supports(facts):
    with pytest.raises(ValueError):
        report_from_facts(facts, "generated")


# Impossible goals fail explicitly rather than silently leaving a rule uncovered.
def test_generator_reports_impossible_goal():
    clauses = [(frozenset({"material_stone", "material_metal"}), "invalid:conflict")]
    with pytest.raises(ValueError, match="no schema-valid report"):
        generate_reports(clauses)


# Generated JSON lines can be fed directly into the normal validation gate.
def test_generated_jsonl_is_valid_input(tmp_path, capsys):
    output = tmp_path / "generated.jsonl"
    main(output)
    assert capsys.readouterr().out == "generated=6\n"
    reports = [json.loads(line) for line in output.read_text().splitlines()]
    assert len(reports) == 6
    for report in reports:
        to_facts(report)
        assert report["goal"] in validate(report)[1]
