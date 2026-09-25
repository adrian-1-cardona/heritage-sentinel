# Adversarial Testing Plan

## Purpose

This week adds no planner features. The goal is to attack the existing planner as if each input were chosen to make it fail, then use repeatable tests to distinguish guarantees from limitations.

Tests will target the generic BFS separately from the restoration and morning problem definitions. A returned action list is not enough to pass: the test must replay it, prove every action was legal when chosen, and prove the final state equals the goal.

## Current contract under test

The current implementation is expected to:

- return `[]` when the start already equals the goal;
- return a shortest plan by number of actions for a finite, unweighted graph;
- return `None` when a finite reachable graph is exhausted without finding the goal;
- expand a discovered state at most once, including across cycles and duplicate transitions; and
- keep action meaning and transition legality inside the supplied callbacks.

The current API assumes that states are hashable and stable, action iterables are finite, callbacks are deterministic enough for visited-state pruning, and goal equality is exact. Action `cost` metadata is not used. These assumptions must be characterized rather than silently mistaken for stronger guarantees.

## Test oracles

The tests will favor semantic properties over one exact action ordering:

1. Replay the plan from the supplied start state.
2. Before each step, assert that the selected action is currently available.
3. Apply the action and continue from the returned state.
4. Assert that the final state equals the goal exactly.
5. Compare plan length with an independently known shortest distance.
6. Count callback invocations where termination or deduplication is part of the claim.

Exact list comparisons will be secondary regression checks for the repository's current deterministic dictionary order.

## Attack matrix

### Priority 0: generic BFS behavior

| ID | Adversarial setup | Expected oracle |
| --- | --- | --- |
| BFS-01 | Make `start == goal`; use callbacks that fail if called. | Return `[]` and call neither callback. |
| BFS-02 | Yield a long branch before a direct edge to the goal. | Return the one-action route, proving FIFO breadth-first behavior rather than first-branch or depth-first behavior. |
| BFS-03 | Add self-loops, a cycle back to the start, and duplicate transitions. | Terminate, expand each distinct state at most once, and return the shortest exit path if one exists. |
| BFS-04 | Use a finite graph in which the goal is unreachable. | Return `None`, not `[]` and not an exception. |
| BFS-05 | Provide two equal-length routes to the same goal. | Return a shortest route; with stable callback order, choose the first yielded tie. Reversing that order may reverse the selected tie but must not change validity or length. |
| BFS-06 | Have `available_actions` raise, then have `apply_action` raise in a separate case. | Propagate the original exception rather than hiding it or returning a false plan. |
| BFS-07 | Use an unhashable start, then a hashable start with an unhashable successor. | Characterize the current boundary with `TypeError`; hashable states are an API precondition. |
| BFS-08 | Let a callback offer an action that teleports directly to the goal. | Characterize that BFS accepts it; edge legality belongs to the callbacks, not the search loop. |
| BFS-09 | Make a one-step route expensive and a multi-step route cheap. | Characterize that BFS chooses fewer actions, not lower total cost. No test may claim cost optimality. |

### Priority 1: problem-definition integration

| ID | Adversarial setup | Expected oracle |
| --- | --- | --- |
| GRAPH-01 | Run the restoration problem and replay the result. | Every prerequisite is satisfied before its action, all four actions occur once, and the final state is `GOAL`. |
| GRAPH-02 | Run the morning problem and replay the result. | `leave_home` occurs only after both prerequisites, all three actions occur once, and the final state is `GOAL`. |
| GRAPH-03 | Start each problem from every subset of its known actions, including historically inconsistent subsets. | The planner reaches `GOAL` in exactly the number of missing actions; this documents that initial history is not validated. |
| GRAPH-04 | Add an unknown value to an otherwise valid state. | Characterize exact goal equality: monotone transitions cannot remove the value, so search returns `None`. |
| GRAPH-05 | Call `apply_action` directly with an unavailable or unknown action. | Characterize that the callback adds it; callers must obtain legal actions from `available_actions`. |
| GRAPH-06 | Check action metadata independently. | `GOAL` equals the action keys, every prerequisite names a defined action, costs are positive numbers, and all actions are reachable from the empty state. |
| GRAPH-07 | Reverse or shuffle action enumeration without changing the graph. | Any returned plan remains legal and shortest even if a different valid topological ordering wins a tie. |

### Priority 2: bounded worst cases and metamorphic checks

| ID | Adversarial setup | Expected oracle |
| --- | --- | --- |
| META-01 | Rename every state and action through a one-to-one mapping. | Reachability and shortest-plan length stay unchanged; the returned plan maps back to a valid original plan. |
| META-02 | Generate small deterministic finite graphs and compare against an independent reference BFS. | Reachability and shortest distance agree for every generated case. A fixed seed makes failures reproducible. |
| STRESS-01 | Model a modest number of independent mandatory actions, creating a powerset state graph. | Return a valid plan of the expected length, never expand a state twice, and keep the test bounded. Record the near-`2^n` growth rather than using a machine-dependent speed threshold. |
| STRESS-02 | Run an infinite-state graph only in an isolated subprocess with a timeout. | The timeout demonstrates that the current API has no search bound. This is a documented limitation, not a normal in-process test that can hang the suite. |

## Test organization

The planned suite will use Python's standard `unittest` library so testing adds no dependency:

- `tests/test_planner.py`: synthetic graph attacks against `bfs_search`;
- `tests/test_restoration_graph.py`: restoration metadata, exhaustive subsets, and plan replay;
- `tests/test_morning_graph.py`: second-domain replay and exhaustive subsets; and
- `tests/helpers.py`: replay assertions and small reference-graph utilities.

The intended one-shot command is:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Execution order

1. Build replay and callback-counting helpers.
2. Lock down zero-step, shortest-path, unreachable, cycle, duplicate-state, and tie behavior.
3. Add malformed-state and callback-failure characterization tests.
4. Add restoration and morning integration tests over every known state subset.
5. Add metadata, metamorphic, and small generated-graph checks.
6. Run the bounded stress case last; keep the infinite-state diagnostic outside the normal suite.

## Exit criteria

Testing is complete only when:

- every Priority 0 case has an explicit assertion and passes according to the current contract;
- both supplied problem plans pass semantic replay from every known state subset;
- cycles, duplicate transitions, and unreachable goals terminate within deterministic bounds;
- tests do not depend on one valid tie ordering unless that ordering is the behavior under test;
- unsupported behavior—unhashable states, illegal callbacks, ignored costs, and unbounded search—is visible in named characterization tests or documentation; and
- production files under `src/` remain unchanged during this testing-only week.
