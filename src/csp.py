# csp.py — generic CSP solver. No statues, cracks, or pigment allowed here.
import random

def consistent(assignment, constraints):
    """False if any constraint whose variables are all assigned is violated."""
    for scope, check in constraints:
        if all(v in assignment for v in scope):
            if not check(*[assignment[v] for v in scope]):
                return False
    return True


def backtracking_search(variables, domains, constraints, seed=0, all_solutions=False):
    """Return a list of solutions (dicts). One solution unless all_solutions=True.
    An empty list means no solution exists."""
    rng = random.Random(seed)
    solutions = []

    def backtrack(assignment):
        if len(assignment) == len(variables):
            solutions.append(dict(assignment))
            return not all_solutions        # stop early unless collecting all

        var = next(v for v in variables if v not in assignment)
        values = list(domains[var])
        rng.shuffle(values)                 # seeded tie-breaking

        for value in values:
            # TODO: assign `value` to `var`. If the assignment is still
            # consistent, recurse; if the recursion returns True, return True.
            # Otherwise undo the assignment and try the next value.
            ...
        return False

    backtrack({})
    return solutions