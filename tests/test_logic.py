from logic import explain, forward_chain


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
