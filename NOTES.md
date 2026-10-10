LabP1: I swapped main.py from restoration_graph to morning_graph, and planner.py did not need to change. The planner only uses the start state, goal state, and the available_actions and apply_action functions it receives, so it does not need to know what any action means. Each problem file owns its actions and prerequisites, while planner.py only handles the BFS process.

LabP2: test_no_solution_returns_none caught an assumption I had wrong: bfs_search already exhausts the finite search space and returns None for an unreachable goal instead of hanging.

LabP3: When I kept VARIABLES as list(ACTIONS.keys()), I got the same plan all three times. When I changed it to list(set(ACTIONS.keys())), six separate runs gave me four different valid plans even though the seed stayed 42. The set changed order between Python processes because string hashes are randomized, and that changed which variables the solver tried first. The seed only controlled the shuffles inside backtracking_search, not the set order, so changing VARIABLES back to a list made the full run reproducible.

The Lab 2 oracle was correct for the rules I had then because it checked prerequisites, duplicates, and completeness. Lab 3 added the tranche rule, so the old oracle accepted stabilize_base followed by seal_crack even though those first two actions cost 5 and the cap is 4. This showed me that tests can get stale when requirements change: passing old tests only proves the old rules, so tests and their helper functions have to change with the specification.

Lab 4 predictions, recorded before running validation:

| Report | Expected result | Reason |
| --- | --- | --- |
| r1 | Accept | Structural damage is marked major. |
| r2 | Reject | Structural risk is marked minor. |
| r3 | Accept | Rot is compatible with wood. |
| r4 | Reject | Rot is incompatible with inorganic material. |
| r5 | Accept | Corrosion is compatible with metal. |
| r6 | Reject | Corrosion is incompatible with organic material. |
| r7 | Accept | Empty damage agrees with severity none. |
| r8 | Reject | Listed damage contradicts severity none. |
| r9 | Reject | Rot on inorganic material and structural risk marked minor. |
| r10 | Reject | Schema error: missing severity. |
| r11 | Reject | Schema error: unknown material. |

Lab 4 self-check: the starter run returned accepted=4 rejected=7, matching all predictions above; there were no disagreements. The r2 proof matches the supplied example, r9 has both semantic violations, and r10/r11 have schema reasons with no logical proofs.

Part B, termination: each changing pass strictly grows the known-symbol set, and only finitely many initial facts and clause conclusions can enter it. Once no new symbol can be added, the loop stops, including when rules form cycles.

Part B, sorted premises: sorting gives proof branches a stable order despite randomized set iteration across Python processes, keeping rejection logs reproducible like the Lab 3 variable-order fix.

Proof ordering: the scratch experiment with a → goal and b → goal produced the same conclusions but different first-fired proofs after reversing the rules, so an audited log needs the rule version and a stable clause order to reproduce its recorded justification.

Custom rule 1 rejects corrosion on ceramic (r12): this report vocabulary treats corrosion as metal deterioration, so a corroding metal fitting should be reported as metal rather than as its ceramic substrate. Changing the material to metal or the damage to fading gives accepted near-misses.
