# Heritage Sentinel
Heritage Sentinel is a small AI system that assesses damage to a cultural heritage artifact with a damage classifier, plans its restoration with a restoration planner, and tracks its history with a provenance graph.

## Status
Completed Lab 5: layered validation that rejects impossible reports, quarantines improbable ones, and tests whole batches for drift.

## Project structure
- `data/`: artifact inputs and project data.
- `src/restoration_graph.py`: restoration actions, prerequisites, and states.
- `src/planner.py`: problem-agnostic BFS.
- `src/logic.py`: domain-independent forward and backward chaining.
- `src/prob.py`: domain-independent smoothed fitting, chi-square, and percentiles.
- `src/report_rules.py`: validation vocabulary, rules, and report construction.
- `src/validate.py`: report schema checks and rejection logs.
- `src/generate_reports.py`: minimal triggering reports for every rejection rule.
- `src/report_model.py`: the Bayesian network over a report and its threshold calibration.
- `src/quality.py`: the accept / quarantine / reject pipeline and the batch drift checks.
- `tools/make_data.py`: seeded generator for the reference and incoming batches.
- `src/main.py`: runs the restoration planner.
- `src/morning_graph.py`: second problem used for the modularity check.
- `tests/`: project tests.
- `NOTES.md`: modularity reflection.

## Modules
- Damage classifier: will assess visible artifact damage.
- Restoration planner: finds valid action orders with BFS.
- Provenance graph: will record the artifact's history and restoration work.


## Run the planner
```bash
python3 src/main.py
```

Expected output:
```text
Restoration plan: ['stabilize_base', 'seal_crack', 'clean_surface', 'restore_pigment']
```

## Validate reports

```bash
python3 src/validate.py
python3 src/generate_reports.py
python3 -m pytest -q
```

The original eleven reports produce `accepted=4 rejected=7`. The full thirteen produce `accepted=6 rejected=7` and write reasons and proofs to `data/rejected.log.jsonl`. The generator writes four minimal triggering reports to `data/generated_reports.jsonl`, one per rejection rule.

Lab 4 had two more rules, `invalid:corrosion_on_ceramic` and `invalid:crack_on_textile`. Lab 5's trusted reference data contains cracked textiles, so those rules called 6 trusted reports impossible. Both were claims about rarity rather than impossibility, so they moved to the likelihood layer below, which now quarantines the same reports instead of rejecting them.

Optional input and log paths are positional arguments to `src/validate.py`; the generator accepts an optional output path. The Lab 4 release is tagged `v0.4-validated`.

## Check data quality

```bash
python3 tools/make_data.py data
python3 src/quality.py data/incoming_a.jsonl
python3 src/quality.py data/incoming_b.jsonl
```

Each report gets one of three verdicts. The schema and logic gate rejects what is impossible, a likelihood below the calibrated threshold quarantines what is merely improbable, and a chi-square test on the whole batch catches a mix that has drifted away from the reference:

```text
{"summary": {"accept": 100, "quarantine": 3, "reject": 2}, "drift": {"material_mix": [5.28, 18.467, false], "severity_mix": [3.25, 13.816, false]}, "threshold": -6.56}
{"summary": {"accept": 100}, "drift": {"material_mix": [155.24, 18.467, true], "severity_mix": [7.19, 13.816, false]}, "threshold": -6.56}
```

Batch B is the point of the batch layer: all 100 of its reports are individually accepted, and its material mix is still wrong by a statistic of 155.24 against a critical value of 18.467. Non-accepted reports go to `data/incoming_a.quality.log.jsonl` and `data/incoming_b.quality.log.jsonl`, with the second empty by design.

The threshold is calibrated rather than chosen: it is the 2nd percentile of the reference reports' own log-likelihoods, which puts 8 of those 400 below it. On 2000 fresh reports the quarantine rate comes out at 2.15%. The Lab 5 release is tagged `v0.5-data-checked`.
