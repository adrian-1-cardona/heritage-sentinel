# Heritage Sentinel

Heritage Sentinel is a small AI system that assesses damage to a cultural heritage artifact with a damage classifier, plans its restoration with a restoration planner, and tracks its history with a provenance graph.

## Status

The Week 1 skeleton is complete, and the Week 2 restoration planner is implemented.

- Damage classifier: not started
- Restoration planner: implemented with problem-agnostic BFS
- Provenance graph: not started

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

## Version control

Versioning starts with the skeleton so each project decision can be traced from the beginning.

## Modularity

The search algorithm stays separate from the problem it solves so each part can be understood, tested, and reused on its own.

## Current scope

Week 1 set up the repository. Week 2 adds the generic BFS planner, the restoration problem, and a second problem used to check modularity.

## Run the planner

```bash
python3 src/main.py
```

Expected output:

```text
Restoration plan: ['stabilize_base', 'seal_crack', 'clean_surface', 'restore_pigment']
```

## Checked results

The restoration plan reaches the goal with every prerequisite completed first. For the modularity check, I changed only `main.py` to use `morning_graph` and got `['pack_lunch', 'fill_bottle', 'leave_home']`. `planner.py` stayed unchanged, and `main.py` was switched back to the restoration problem afterward.
