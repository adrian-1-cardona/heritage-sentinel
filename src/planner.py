# planner.py — search algorithm only. No mention of statues, cracks, or pigment allowed here.
from collections import deque


def bfs_search(start, goal, available_actions, apply_action):
    frontier = deque([(start, [])])
    visited = {start}
    while frontier:
        state, path = frontier.popleft()
        if state == goal:
            return path
        for action in available_actions(state):
            next_state = apply_action(state, action)
            if next_state not in visited:
                visited.add(next_state)
                frontier.append((next_state, path + [action]))
    return None  # no valid sequence exists
