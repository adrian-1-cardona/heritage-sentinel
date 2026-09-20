ACTIONS = {
    "pack_lunch": {"requires": set(), "cost": 1},
    "fill_bottle": {"requires": set(), "cost": 1},
    "leave_home": {"requires": {"pack_lunch", "fill_bottle"}, "cost": 1},
}

GOAL = frozenset(ACTIONS.keys())
START = frozenset()


def available_actions(state):
    return [a for a, info in ACTIONS.items()
            if a not in state and info["requires"].issubset(state)]


def apply_action(state, action):
    return state | {action}
