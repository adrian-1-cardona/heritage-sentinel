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

Correction from Lab 5: those two numbers are the Lab 4 record as it stood at the v0.4-validated tag, and since Lab 5 retired two of those rules the current repo has 4 rejection goals and the same 13 reports give accepted=6 rejected=7.

Lab 5 guesses, before I ran it: a-odd1 quarantine since stone with corrosion breaks none of my rules but never appears in the reference, a-odd2 and a-odd3 reject because my own Lab 4 rules call corroded ceramic and cracked textile impossible, a-bad1 reject on rot_on_inorganic, and a-bad2 reject on schema since marble is not in the vocabulary.

Lab 5 self check: both batches reproduce the handout at threshold -6.56 with 8 of the 400 reference reports below it, and the only difference in the printed line is the severity_mix key Part E tells me to add to batch_drift after Part C had already frozen its expected output, so the summaries, the material_mix numbers and the threshold are byte-identical and test_self_check_matches_the_handout_byte_for_byte pins them against the two handout strings.

Predictions: I was right on a-odd1, a-bad1 and a-bad2 and wrong on a-odd2 and a-odd3, and the pipeline was right because my own rules were the problem, since the reference data holds 6 cracked textiles that crack_on_textile was calling impossible and both retired rules were claims about rarity that the likelihood layer now handles at -8.92 and -9.24.

Independence: given the material the model treats crack and loose_base as unrelated, which is wrong about real artifacts because a base that has come loose puts an object under exactly the stress that cracks it, though I cannot show it from this file since the generator draws each damage type independently given material, and the stretch table confirms that by moving the held-out rate only from 2.15% to 2.25% when I drop the assumption.

Parameters: 4 for P(material) plus 25 for the five Bernoulli damage tables across five materials plus 6 for P(severity | bucket) is 35, which only the factorisation makes affordable since the full joint would need 5 * 2**5 * 3 = 480 cells for 400 reports, and 400 carries the 35 because the thinnest material, textile, still has 37 rows behind its 5 damage rates, where 40 reports would leave textile about 4 and I would be calibrating a threshold against alpha and calling it data.

Smoothing: with alpha=0 my model dies on stone with corrosion because that pair never appears in the reference and log(0) is undefined, which is the same failure production hits the first time the vocabulary gains a word or the first survey from a new region lands and one unrecorded pair takes down the whole batch instead of being flagged as the unusual thing it is.

Why batch B needed a batch check: all 100 of its reports are ordinary wood or textile records that pass individually, and drift is a property of the mix rather than of any record, so no record-level check can ever see it and the only way to catch it is to count a whole batch against what the reference says those counts should be.

Calibration: the threshold is the 2nd percentile of scores the model was fitted on so it is optimistic by construction, and the gap stayed small only because 35 count-based parameters over 400 reports cannot memorise individual rows, which keeps in-sample and fresh scores on nearly the same distribution and landed the held-out rate at 2.15% against the 2% I asked for, whereas it would widen as the parameter count approached the sample size and the model began fitting the particular 400 instead of the process behind them, pushing its in-sample scores up so a percentile taken from them sits too high, which is why the honest fix is to calibrate on reports the model never saw.

Quarantine versus reject: a-odd3 scores -9.24 and gets held, so a surveyor who finds a genuinely rare cracked textile with a loose base has a correct report sitting in a queue instead of in the data, which taxes honest rarity and quietly teaches people to round unusual findings toward usual ones to get through, and if losing a rare discovery were worse than admitting a typo I would drop q from 0.02 to about 0.002 and pay for it in typos, since fewer held reports means more wrong ones flow into Week 6's training data and the quarantine log stops being short enough for a human to work through.

Stretch: conditioning loose_base on crack as well as material lifts a-odd3 from -9.24 to -7.66 because the reference has 6 cracked textiles with sound bases to learn from and only moves the threshold from -6.56 to -6.52, so a-odd3 stays quarantined without being an extreme outlier, the held-out rate barely shifts from 2.15% to 2.25%, and the count goes from 35 to 40 parameters which 400 reports still supports, though textile-with-crack at 6 rows is now the thinnest cell and the first I would expect to break.
