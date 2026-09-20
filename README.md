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

## Planned modules

- Damage classifier: assesses visible artifact damage.
- Restoration planner: builds a restoration plan from the assessment.
- Provenance graph: records the artifact's history and restoration work.

## Version control

Versioning starts with the skeleton so each project decision can be traced from the beginning.

## Modularity

The search algorithm will stay separate from the artifact problem it solves so each part can be understood, tested, and reused on its own.

## Current scope

Week 1 set up the repository. Week 2 adds the generic BFS planner, the restoration problem, and a second problem used to check modularity.
