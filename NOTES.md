LabP1: I swapped main.py from restoration_graph to morning_graph, and planner.py did not need to change. The planner only uses the start state, goal state, and the available_actions and apply_action functions it receives, so it does not need to know what any action means. Each problem file owns its actions and prerequisites, while planner.py only handles the BFS process.

LabP2: test_no_solution_returns_none caught an assumption I had wrong: bfs_search already exhausts the finite search space and returns None for an unreachable goal instead of hanging.

LabP3: When I kept VARIABLES as list(ACTIONS.keys()), I got the same plan all three times. When I changed it to list(set(ACTIONS.keys())), six separate runs gave me four different valid plans even though the seed stayed 42. The set changed order between Python processes because string hashes are randomized, and that changed which variables the solver tried first. The seed only controlled the shuffles inside backtracking_search, not the set order, so changing VARIABLES back to a list made the full run reproducible.

The Lab 2 oracle was correct for the rules I had then because it checked prerequisites, duplicates, and completeness. Lab 3 added the tranche rule, so the old oracle accepted stabilize_base followed by seal_crack even though those first two actions cost 5 and the cap is 4. This showed me that tests can get stale when requirements change: passing old tests only proves the old rules, so tests and their helper functions have to change with the specification.

Lab 4 predictions, before I ran anything: accept r1, r3, r5, r7 and reject the other seven, with r9 picking up two reasons and r10 and r11 failing on schema instead of logic.

Lab 4 self-check: the starter run gave accepted=4 rejected=7 and matched all eleven guesses, so no disagreements to settle. r2's proof printed exactly like the lab's example, r9 listed both violations, and r10 and r11 came back with schema reasons and empty proofs, which is what I wanted since a missing field is not something the rules should be reasoning about.

Part B, why it terminates: known only ever grows, and it is capped at my starting facts plus one symbol per clause conclusion, so every pass that sets changed adds at least one symbol to a finite set and eventually nothing new fits. Cycles like a implies b implies a die at the "conclusion not in known" check.

Part B, why explain sorts: iterating a set hands me whatever order hash randomization picked that run, same trap as VARIABLES in Lab 3, so sorted(premises) pins the branch order and the same rejection always prints the same proof.

Proof ordering: with two rules deriving the same goal, known stayed identical but why kept whichever fired first, so reversing the clause list flipped the proofs. The verdict is stable and the justification is not, so an audited log has to record the rule version and the clause order or I cannot reproduce the explanation I handed somebody months ago.

My two rules: r12 rejects corrosion on ceramic, because corrosion is a metal thing and a corroding fitting should be reported as metal rather than as the ceramic it sits in. r13 rejects cracks on textile, because fabric tears instead of fracturing. Both near-misses get accepted, so each rule really needs both premises.

Part E: a Horn clause can only say "if all of these facts hold, conclude this," so there is no way to say "and no damage_ fact is present," and severity_major on its own tells me nothing about what is missing. I would either have to_facts emit a no_damage fact for an empty list, which is cheap but bakes a closed-world assumption into the schema layer, or add real negation, which costs monotonicity: adding a fact could then retract a conclusion, so forward_chain needs a proper fixpoint strategy and my termination argument above stops holding.

Backward chaining: backward_chain expands a goal into minimal fact sets, cutting cyclic branches and dropping any support that contains a smaller one. It produced a trigger for all six rejection goals, matching my hand-written reports except it picked different materials for none_but_damaged and rot_on_inorganic, so I had not missed a rule. Final batch is 13 reports at accepted=4 rejected=9, and the generated ones live in data/generated_reports.jsonl.
