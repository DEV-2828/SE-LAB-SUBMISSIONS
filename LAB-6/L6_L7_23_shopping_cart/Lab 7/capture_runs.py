"""Capture real subprocess output for the before/after lab evidence."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"


def capture(stage, target=None):
    EVIDENCE.mkdir(exist_ok=True)
    jobs = [("application", [sys.executable, "shopping_cart.py"], "bad\nOFF101\n5\n"),
            ("tests", [sys.executable, "-m", "pytest", "test_shopping_cart.py", "-q", "--tb=short", "--color=no"], None)]
    if stage == "after":
        jobs[1] = ("tests", [sys.executable, "-m", "pytest", "test_shopping_cart.py", "-v", "--tb=short", "--color=no", "--hypothesis-show-statistics"], None)
        jobs.append(("valid_application", [sys.executable, "shopping_cart.py"], "pen:10x2,book:250x1\nOFF20\n560085\n"))
    for label, command, inputs in jobs:
        run = subprocess.run(command, cwd=target or HERE, input=inputs, text=True, capture_output=True, timeout=120, encoding="utf-8", errors="replace")
        data = dict(stage=stage, command=["python", *command[1:]], stdin=inputs, exit_code=run.returncode, stdout=run.stdout, stderr=run.stderr)
        stem = EVIDENCE / f"{stage}_{label}"
        stem.with_suffix(".json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        stem.with_suffix(".txt").write_text(run.stdout + run.stderr, encoding="utf-8")
        print(f"{stage} {label}: exit={run.returncode}")
        print(run.stdout + run.stderr)


if __name__ == "__main__":
    capture(sys.argv[1], Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None)
