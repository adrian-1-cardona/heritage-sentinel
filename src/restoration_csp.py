# restoration_csp.py — problem definition only.
from restoration_graph import ACTIONS

VARIABLES = list(ACTIONS.keys())
DOMAINS = {a: list(range(1, len(VARIABLES) + 1)) for a in VARIABLES}


def build_constraints(actions=ACTIONS, tranche_cap=4):
    constraints = []

    # 1. all-different
    for i, a in enumerate(VARIABLES):
        for b in VARIABLES[i + 1:]:
            constraints.append(((a, b), lambda x, y: x != y))

    # 2. prerequisites
    for action in VARIABLES:
        for required in actions[action]["requires"]:
            constraints.append(
                ((required, action), lambda required_slot, action_slot:
                 required_slot < action_slot)
            )

    # 3. tranche rule
    def within_tranche_cap(*slots):
        return sum(
            actions[action]["cost"]
            for action, slot in zip(VARIABLES, slots)
            if slot <= 2
        ) <= tranche_cap

    constraints.append((tuple(VARIABLES), within_tranche_cap))

    return constraints
