# Heritage Sentinel
Heritage Sentinel is a small AI system that assesses damage to a cultural heritage artifact with a damage classifier, plans its restoration with a restoration planner, and tracks its history with a provenance graph.

## Status
just finished lab p3

## Project structure
- `data/`: artifact inputs and project data.
- `src/restoration_graph.py`: restoration actions, prerequisites, and states.
- `src/planner.py`: problem-agnostic BFS.
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
