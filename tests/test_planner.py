from restoration_graph import ACTIONS, START, GOAL, available_actions, apply_action
from planner import bfs_search


def is_valid_plan(plan, actions=ACTIONS):
    """A plan is valid if every action's prerequisites are satisfied by
    the actions before it, and every required action appears exactly once.
    """
    completed = set()
    for action in plan:
        if action in completed:
            return False
        if not actions[action]["requires"].issubset(completed):
            return False
        completed.add(action)
    return completed == set(actions.keys())


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
