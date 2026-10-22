import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from validate import main


ROOT = Path(__file__).resolve().parents[1]


# Freeze the original eleven reports so later rules can retain the baseline check.
def test_starter_batch_matches_self_check(tmp_path):
    source = tmp_path / "reports.jsonl"
    source.write_text(
        "\n".join((ROOT / "data/reports.jsonl").read_text().splitlines()[:11]) + "\n"
    )
    log = tmp_path / "rejected.jsonl"
    result = subprocess.run(
        [sys.executable, str(ROOT / "src/validate.py"), str(source), str(log)],
        capture_output=True, text=True, check=True, timeout=5,
    )
    assert result.stdout == "accepted=4 rejected=7\n"
    rejected = [json.loads(line) for line in log.read_text().splitlines()]
    assert [report["id"] for report in rejected] == [
        "r2", "r4", "r6", "r8", "r9", "r10", "r11"
    ]
    assert len(rejected[4]["reasons"]) == 2
    assert all(report["proofs"] == {} for report in rejected[-2:])


# A malformed line must be logged while later valid reports still get checked.
def test_malformed_json_does_not_stop_batch(tmp_path):
    source = tmp_path / "reports.jsonl"
    good = (ROOT / "data/reports.jsonl").read_text().splitlines()[0]
    source.write_text("{broken\nnull\n" + good + "\n")
    log = tmp_path / "rejected.jsonl"
    assert main(source, log) == (1, 2)
    rejected = [json.loads(line) for line in log.read_text().splitlines()]
    assert rejected[0] == {
        "id": None, "reasons": ["schema: invalid JSON on line 1"], "proofs": {}
    }
    assert rejected[1]["reasons"] == ["schema: report must be an object"]


# Protect source reports from being overwritten by their own rejection log.
def test_log_cannot_overwrite_reports(tmp_path):
    source = tmp_path / "reports.jsonl"
    source.write_text("original\n")
    with pytest.raises(ValueError, match="different paths"):
        main(source, source)
    assert source.read_text() == "original\n"


# Final totals and checked-in proofs must reproduce across randomized hash seeds.
def test_final_log_is_reproducible(tmp_path):
    expected = (ROOT / "data/rejected.log.jsonl").read_text()
    for seed in ("1", "42", "123"):
        log = tmp_path / f"rejected-{seed}.jsonl"
        result = subprocess.run(
            [sys.executable, str(ROOT / "src/validate.py"),
             str(ROOT / "data/reports.jsonl"), str(log)],
            env={**os.environ, "PYTHONHASHSEED": seed},
            capture_output=True, text=True, check=True, timeout=5,
        )
        assert result.stdout == "accepted=6 rejected=7\n"
        assert log.read_text() == expected


# Keep the cycle check isolated so a termination regression cannot hang pytest.
def test_cycle_terminates_with_process_timeout():
    result = subprocess.run(
        [sys.executable, "-c",
         "from logic import forward_chain; "
         "assert forward_chain({'a'}, [(frozenset({'a'}), 'b'), "
         "(frozenset({'b'}), 'a')])[0] == {'a', 'b'}"],
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        capture_output=True, text=True, check=True, timeout=5,
    )
    assert result.returncode == 0
