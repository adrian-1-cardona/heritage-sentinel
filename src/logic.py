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
