# Heritage Sentinel
Heritage Sentinel is a small AI system that assesses damage to a cultural heritage artifact with a damage classifier, plans its restoration with a restoration planner, and tracks its history with a provenance graph.

## Status
Completed Lab 4: schema validation, explainable logical rejection, and backward-chaining report generation.

## Project structure
- `data/`: artifact inputs and project data.
- `src/restoration_graph.py`: restoration actions, prerequisites, and states.
- `src/planner.py`: problem-agnostic BFS.
- `src/logic.py`: domain-independent forward and backward chaining.
- `src/report_rules.py`: validation vocabulary, rules, and report construction.
- `src/validate.py`: report schema checks and rejection logs.
- `src/generate_reports.py`: minimal triggering reports for every rejection rule.
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

The original eleven reports produce `accepted=4 rejected=7`. With the two custom-rule reports, validation produces `accepted=4 rejected=9` and writes reasons and proofs to `data/rejected.log.jsonl`. The generator writes six minimal triggering reports to `data/generated_reports.jsonl`.

Optional input and log paths are positional arguments to `src/validate.py`; the generator accepts an optional output path. The Lab 4 release is tagged `v0.4-validated`.
