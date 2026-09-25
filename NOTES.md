I swapped main.py from restoration_graph to morning_graph, and planner.py did not need to change. The planner only uses the start state, goal state, and the available_actions and apply_action functions it receives, so it does not need to know what any action means. Each problem file owns its actions and prerequisites, while planner.py only handles the BFS process.

`test_no_solution_returns_none` caught an assumption I had wrong: `bfs_search` already exhausts the finite search space and returns `None` for an unreachable goal instead of hanging.
