# prob.py — generic probability helpers. No heritage vocabulary allowed here.
from collections import Counter


# Add-alpha counts keep every domain value possible, so log() never sees zero.
def fit_categorical(observations, domain, alpha=1.0):
    """P(value) with add-alpha (Laplace) smoothing. Returns {value: prob}.
    Every value in `domain` gets nonzero probability, even if never observed."""
    counts = Counter(observations)
    total = sum(counts.values()) + alpha * len(domain)
    return {value: (counts[value] + alpha) / total for value in domain}


def fit_conditional(pairs, parent_domain, child_domain, alpha=1.0):
    """P(child | parent) from (parent, child) pairs. Returns {parent: {child: prob}}."""
    by_parent = {p: [] for p in parent_domain}
    for parent, child in pairs:
        by_parent[parent].append(child)
    return {p: fit_categorical(by_parent[p], child_domain, alpha) for p in parent_domain}


def chi_square(observed_counts, expected_probs):
    """Pearson chi-square statistic comparing observed counts to expected probabilities."""
    ...


def percentile(values, q):
    """Nearest-rank style: the value at index floor(q * n) of the sorted list."""
    ordered = sorted(values)
    return ordered[min(int(q * len(ordered)), len(ordered) - 1)]
