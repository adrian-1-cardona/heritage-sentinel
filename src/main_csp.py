import json

from csp import backtracking_search
from restoration_csp import VARIABLES, DOMAINS, build_constraints


def main(config_path="config.json"):
    with open(config_path) as f:
        cfg = json.load(f)

    constraints = build_constraints(tranche_cap=cfg["tranche_cap"])
    solutions = backtracking_search(
        VARIABLES,
        DOMAINS,
        constraints,
        seed=cfg["seed"],
    )
    plan = None
    if solutions:
        assignment = solutions[0]
        plan = sorted(assignment, key=assignment.get)

    print(json.dumps({"config": cfg, "plan": plan}))


if __name__ == "__main__":
    main()
