# Infer every reachable symbol, retaining the first proof for each conclusion.
def forward_chain(facts, clauses):
    known = set(facts)
    why = {fact: None for fact in known}
    clauses = list(clauses)
    changed = True
    while changed:
        changed = False
        for premises, conclusion in clauses:
            if conclusion not in known and premises <= known:
                known.add(conclusion)
                why[conclusion] = premises
                changed = True
    return known, why


# Render a proof in a stable order, ending at the supplied facts.
def explain(symbol, why, depth=0):
    pad = "  " * depth
    premises = why[symbol]
    if premises is None:
        return [f"{pad}{symbol}  (given)"]
    lines = [f"{pad}{symbol}  because:"]
    for premise in sorted(premises):
        lines.extend(explain(premise, why, depth + 1))
    return lines


# Keep only inclusion-minimal fact sets, in a reproducible order.
def _minimal_supports(supports):
    unique = set(supports)
    return sorted(
        (support for support in unique if not any(other < support for other in unique)),
        key=lambda support: (len(support), sorted(support)),
    )


# Work backward to enumerate minimal fact sets that can establish a goal.
def backward_chain(goal, clauses, fact_symbols):
    by_conclusion = {}
    for premises, conclusion in clauses:
        by_conclusion.setdefault(conclusion, []).append(premises)
    fact_symbols = set(fact_symbols)

    # Reject cyclic proof branches while retaining independent routes to the goal.
    def prove(symbol, ancestors):
        if symbol in ancestors:
            return []
        supports = [frozenset({symbol})] if symbol in fact_symbols else []
        for premises in by_conclusion.get(symbol, []):
            combinations = [frozenset()]
            for premise in sorted(premises):
                choices = prove(premise, ancestors | {symbol})
                combinations = _minimal_supports(
                    left | right for left in combinations for right in choices
                )
                if not combinations:
                    break
            supports.extend(combinations)
        return _minimal_supports(supports)

    return prove(goal, set())
