import pytest

from logic import backward_chain, forward_chain


# Enumerate alternative proofs and remove fact sets with redundant assumptions.
def test_backward_transitive_alternatives_and_minimality():
    clauses = [
        (frozenset({"a"}), "b"),
        (frozenset({"b"}), "goal"),
        (frozenset({"a", "c"}), "goal"),
        (frozenset({"d", "e"}), "goal"),
    ]
    supports = backward_chain("goal", clauses, {"a", "c", "d", "e"})
    assert supports == [frozenset({"a"}), frozenset({"d", "e"})]
    assert backward_chain("goal", clauses[::-1], {"a", "c", "d", "e"}) == supports
    for support in supports:
        assert "goal" in forward_chain(support, clauses)[0]
        for fact in support:
            assert "goal" not in forward_chain(support - {fact}, clauses)[0]


# Shared assumptions must be combined once rather than counted repeatedly.
def test_backward_shared_premises():
    clauses = [
        (frozenset({"a"}), "left"), (frozenset({"a"}), "right"),
        (frozenset({"left", "right"}), "goal"),
    ]
    assert backward_chain("goal", clauses, {"a"}) == [frozenset({"a"})]


# A cycle with an external fact can be proved; an unsupported cycle cannot.
def test_backward_cycles():
    clauses = [(frozenset({"a"}), "b"), (frozenset({"b"}), "a")]
    assert backward_chain("b", clauses, {"a"}) == [frozenset({"a"})]
    assert backward_chain("b", clauses, set()) == []
    clauses.append((frozenset({"seed"}), "a"))
    assert backward_chain("b", clauses, {"seed"}) == [frozenset({"seed"})]


# All combinations of alternative premise proofs must be considered.
def test_backward_combines_alternatives():
    clauses = [
        (frozenset({"a"}), "left"), (frozenset({"b"}), "left"),
        (frozenset({"c"}), "right"), (frozenset({"d"}), "right"),
        (frozenset({"left", "right"}), "goal"),
    ]
    assert set(backward_chain("goal", clauses, {"a", "b", "c", "d"})) == {
        frozenset({left, right}) for left in ("a", "b") for right in ("c", "d")
    }


# Facts, unconditional clauses, and unknown goals cover the recursion boundaries.
@pytest.mark.parametrize("goal,clauses,facts,expected", [
    ("a", [], {"a"}, [frozenset({"a"})]),
    ("a", [], set(), []),
    ("a", [(frozenset(), "a")], set(), [frozenset()]),
    ("a", [(frozenset(), "a")], {"a"}, [frozenset()]),
])
def test_backward_boundaries(goal, clauses, facts, expected):
    assert backward_chain(goal, clauses, facts) == expected
