from restoration_graph import ACTIONS, START, GOAL, available_actions, apply_action
from planner import bfs_search


def is_valid_plan(plan, actions=ACTIONS, tranche_cap=None):
    """Return whether a plan is complete and respects all active rules.

    When provided, ``tranche_cap`` limits the combined cost of the first
    two actions.
    """
    completed = set()
    tranche_cost = 0

    for slot, action in enumerate(plan, start=1):
        if action in completed:
            return False
        if not actions[action]["requires"].issubset(completed):
            return False
        if tranche_cap is not None and slot <= 2:
            tranche_cost += actions[action]["cost"]
        completed.add(action)

    if completed != set(actions.keys()):
        return False
    return tranche_cap is None or tranche_cost <= tranche_cap


def test_finds_a_valid_plan():
    plan = bfs_search(START, GOAL, available_actions, apply_action)

    assert plan is not None
    assert is_valid_plan(plan)


def test_trivial_already_done():
    plan = bfs_search(GOAL, GOAL, available_actions, apply_action)

    assert plan == []


def test_plan_has_no_duplicate_actions():
    plan = bfs_search(START, GOAL, available_actions, apply_action)

    assert plan is not None
    assert is_valid_plan(plan)
    assert len(plan) == len(set(plan))


def test_no_solution_returns_none():
    impossible_goal = GOAL | {"missing_action"}

    plan = bfs_search(START, impossible_goal, available_actions, apply_action)

    assert plan is None


def test_large_action_set_terminates():
    from time import perf_counter

    large_actions = {}
    for index in range(20):
        action = f"action_{index}"
        prerequisites = set() if index == 0 else {f"action_{index - 1}"}
        large_actions[action] = {"requires": prerequisites, "cost": 1}

    def synthetic_available_actions(state):
        return [
            action
            for action, details in large_actions.items()
            if action not in state and details["requires"].issubset(state)
        ]

    def synthetic_apply_action(state, action):
        return state | {action}

    start = frozenset()
    goal = frozenset(large_actions)
    started_at = perf_counter()
    plan = bfs_search(
        start,
        goal,
        synthetic_available_actions,
        synthetic_apply_action,
    )
    elapsed = perf_counter() - started_at

    assert plan is not None
    assert is_valid_plan(plan, large_actions)
    assert elapsed < 2.0
