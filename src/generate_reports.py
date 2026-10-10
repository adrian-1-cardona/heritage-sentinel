import json
import sys

from logic import backward_chain, forward_chain
from report_rules import CLAUSES, FACT_SYMBOLS, report_from_facts
from validate import to_facts


# Generate the smallest schema-valid report for each rejection goal.
def generate_reports(clauses=None):
    clauses = list(CLAUSES if clauses is None else clauses)
    reports = {}
    goals = sorted({goal for _, goal in clauses if goal.startswith("invalid:")})
    for goal in goals:
        candidates = []
        for support in backward_chain(goal, clauses, FACT_SYMBOLS):
            try:
                report = report_from_facts(support, f"generated-{goal[8:]}")
            except ValueError:
                continue
            if goal in forward_chain(to_facts(report), clauses)[0]:
                candidates.append(report)
        if not candidates:
            raise ValueError(f"no schema-valid report can trigger {goal}")
        reports[goal] = min(
            candidates, key=lambda report: (len(report["damage"]), sorted(to_facts(report)))
        )
    return reports


# Save one generated report per rule, including its intended rejection goal.
def main(out="data/generated_reports.jsonl"):
    reports = generate_reports()
    with open(out, "w", encoding="utf-8") as output:
        for goal, report in reports.items():
            output.write(json.dumps({"goal": goal, **report}) + "\n")
    print(f"generated={len(reports)}")


if __name__ == "__main__":
    main(*sys.argv[1:])
