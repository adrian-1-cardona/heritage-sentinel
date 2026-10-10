from report_rules import CLAUSES, DAMAGE, MATERIALS, SEVERITIES


# Keep the starter vocabulary and rule structure explicit.
def test_knowledge_base_structure():
    assert len(MATERIALS) == 5
    assert len(DAMAGE) == 5
    assert len(SEVERITIES) == 3
    assert len(CLAUSES) == 17
    assert len(set(CLAUSES)) == len(CLAUSES)
    assert all(isinstance(premises, frozenset) for premises, _ in CLAUSES)
    assert sum(conclusion.startswith("invalid:") for _, conclusion in CLAUSES) == 6
