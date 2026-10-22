LabP1: I swapped main.py from restoration_graph to morning_graph, and planner.py did not need to change. The planner only uses the start state, goal state, and the available_actions and apply_action functions it receives, so it does not need to know what any action means. Each problem file owns its actions and prerequisites, while planner.py only handles the BFS process.

LabP2: test_no_solution_returns_none caught an assumption I had wrong: bfs_search already exhausts the finite search space and returns None for an unreachable goal instead of hanging.

LabP3: When I kept VARIABLES as list(ACTIONS.keys()), I got the same plan all three times. When I changed it to list(set(ACTIONS.keys())), six separate runs gave me four different valid plans even though the seed stayed 42. The set changed order between Python processes because string hashes are randomized, and that changed which variables the solver tried first. The seed only controlled the shuffles inside backtracking_search, not the set order, so changing VARIABLES back to a list made the full run reproducible.

The Lab 2 oracle was correct for the rules I had then because it checked prerequisites, duplicates, and completeness. Lab 3 added the tranche rule, so the old oracle accepted stabilize_base followed by seal_crack even though those first two actions cost 5 and the cap is 4. This showed me that tests can get stale when requirements change: passing old tests only proves the old rules, so tests and their helper functions have to change with the specification.

Lab 4 guesses, before I ran it: accept r1, r3, r5, r7, reject the rest, r9 with two reasons, r10 and r11 on schema.

Lab 4 self check: the starter run gave accepted=4 rejected=7 and matched every guess, so no disagreements. r2's proof matched the lab's example and the schema errors came back with no proofs, which is right since a missing field is not the rules' job.

Part B, why it terminates: known only grows, and it is capped at my facts plus one symbol per clause conclusion, so eventually a pass adds nothing and the loop quits. Cycles die at the "conclusion not in known" check. Set order shifts with hash randomization between runs, same trap as VARIABLES in Lab 3, so sorting keeps the same rejection printing the same proof.

Proof ordering: two rules deriving one goal gave me identical known but different why depending on which fired first, so an audited log needs the rule version and clause order pinned down.

My two rules: r12 rejects corrosion on ceramic, since corrosion is a metal thing. r13 rejects cracks on textile, since fabric tears instead of fracturing. Both near misses get accepted, so each rule needs both premises.

Part E: a Horn clause only says "if these facts hold, conclude this," so I cannot say "and no damage fact is present," and severity_major alone tells me nothing about what is missing. I would either have to_facts emit a no_damage fact for an empty list, which bakes a closed world assumption into the schema layer, or add real negation, which costs monotonicity and breaks the termination argument above.

Backward chaining: backward_chain expands a goal into minimal fact sets and found a trigger for all six rejection goals, so I had not missed a rule. Final batch is 13 reports at accepted=4 rejected=9, generated ones in data/generated_reports.jsonl.

Lab 5 guesses, before I ran it: a-odd1 quarantine, since stone with corrosion breaks none of my rules but no reference report pairs them. a-odd2 and a-odd3 reject, because my own Lab 4 rules call corrosion on ceramic and cracks on textile impossible. a-bad1 reject on rot_on_inorganic, a-bad2 reject on schema since marble is not in the vocabulary.

Lab 5 self check: both batches matched the handout exactly, at threshold -6.56 with 8 of the 400 reference reports below it, but only after I retired two of my own Lab 4 rules.

Predictions: I was right on a-odd1, a-bad1 and a-bad2, and wrong on a-odd2 and a-odd3, which I expected my own custom rules to reject. The pipeline was right and my rules were wrong, because the reference data contains 6 textile reports with cracks, so crack_on_textile was calling trusted data impossible, and corroded ceramic is unusual rather than contradictory. Both rules were claims about rarity, which is this lab's job, so they moved out of the logic layer and the likelihood layer now catches those two at -8.92 and -9.24 instead.

Independence: given the material, the model treats crack and loose_base as unrelated, but a base that has come loose puts the object under exactly the stress that cracks it, so the pair turns up more often than the product of its two rates. That is the same pair my Lab 4 structural_risk rule was written for, so the model charges a-odd3 for both surprises separately and scores it lower than it deserves.

Parameters: 4 for P(material), 25 for the five Bernoulli damage tables across five materials, and 6 for P(severity | bucket), which is 35. 400 reports is enough because the thinnest material, textile, still has 37 rows to estimate its 5 damage rates from. With 40 reports textile would get about 4, so every textile probability would be mostly whatever alpha says, and I would then calibrate a threshold against that noise and call it data.
