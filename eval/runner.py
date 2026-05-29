"""
eval/runner.py — KhamLao evaluation harness (quality layer Phase 3).

Scores a model's Lao output against eval/test_set.json. Two modes:

  1. Offline (default): score pre-generated responses from a JSONL file.
     Each line: {"id": "<test id>", "response": "<model Lao output>"}

  2. Live: pass --model-cmd to shell out to any CLI that takes a prompt on
     stdin and prints the Lao response to stdout (e.g. gemini, a wrapper script).

For each test it runs khamlao_checker.check() on the response, then applies the
test's expect_contains / forbid_contains assertions. Output is a JSON report
plus a console summary (mean score, Thai-leak rate, per-category pass rate).

Usage:
    python eval/runner.py --responses eval/sample_responses.jsonl
    python eval/runner.py --responses out.jsonl --output reports/run.json
    python eval/runner.py --model-cmd "gemini -p" --output reports/gemini.json
    python eval/runner.py --compare reports/a.json reports/b.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from khamlao_checker import check  # noqa: E402

ROOT = Path(__file__).resolve().parent
TEST_SET = ROOT / "test_set.json"


def load_tests() -> list[dict]:
    return json.loads(TEST_SET.read_text(encoding="utf-8"))["tests"]


def load_responses(path: Path) -> dict[str, str]:
    resp = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        resp[rec["id"]] = rec["response"]
    return resp


def run_model(cmd: str, prompt: str) -> str:
    result = subprocess.run(
        cmd, input=prompt, capture_output=True, text=True,
        encoding="utf-8", shell=True, timeout=120,
    )
    return result.stdout.strip()


def grade(test: dict, response: str) -> dict:
    report = check(response)
    missing = [s for s in test.get("expect_contains", []) if s not in response]
    forbidden = [s for s in test.get("forbid_contains", []) if s in response]
    assertions_ok = not missing and not forbidden
    # A test passes if assertions hold AND the checker score is acceptable.
    passed = assertions_ok and report["score"] >= 0.8 and not response.strip() == ""
    return {
        "id": test["id"],
        "category": test["category"],
        "response": response,
        "score": report["score"],
        "register": report["register"],
        "thai_script_chars": report["thai_script"]["count"],
        "issues": report["issues"],
        "missing_expected": missing,
        "found_forbidden": forbidden,
        "passed": passed,
    }


def aggregate(graded: list[dict]) -> dict:
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for g in graded:
        by_cat[g["category"]].append(g)
    n = len(graded) or 1
    return {
        "n_tests": len(graded),
        "n_passed": sum(g["passed"] for g in graded),
        "pass_rate": round(sum(g["passed"] for g in graded) / n, 3),
        "mean_score": round(sum(g["score"] for g in graded) / n, 3),
        "thai_leak_rate": round(sum(1 for g in graded if g["thai_script_chars"]) / n, 3),
        "by_category": {
            cat: {
                "n": len(gs),
                "passed": sum(g["passed"] for g in gs),
                "mean_score": round(sum(g["score"] for g in gs) / len(gs), 3),
            }
            for cat, gs in sorted(by_cat.items())
        },
    }


def print_summary(summary: dict, graded: list[dict]) -> None:
    print(f"\n=== KhamLao eval: {summary['n_passed']}/{summary['n_tests']} passed "
          f"({summary['pass_rate']:.0%})  mean_score={summary['mean_score']}  "
          f"thai_leak_rate={summary['thai_leak_rate']:.0%} ===\n")
    print(f"{'category':<22}{'pass':>8}{'mean':>8}")
    for cat, c in summary["by_category"].items():
        print(f"{cat:<22}{c['passed']}/{c['n']:<6}{c['mean_score']:>8}")
    failures = [g for g in graded if not g["passed"]]
    if failures:
        print("\nfailures:")
        for f in failures:
            reasons = []
            if f["missing_expected"]:
                reasons.append(f"missing {f['missing_expected']}")
            if f["found_forbidden"]:
                reasons.append(f"forbidden {f['found_forbidden']}")
            if f["score"] < 0.8:
                reasons.append(f"score {f['score']}")
            print(f"  {f['id']}: {'; '.join(reasons)}")


def compare(path_a: Path, path_b: Path) -> None:
    a = json.loads(path_a.read_text(encoding="utf-8"))
    b = json.loads(path_b.read_text(encoding="utf-8"))
    sa, sb = a["summary"], b["summary"]
    print(f"\n{'metric':<18}{path_a.stem:>14}{path_b.stem:>14}{'Δ':>10}")
    for k in ("pass_rate", "mean_score", "thai_leak_rate"):
        delta = round(sb[k] - sa[k], 3)
        print(f"{k:<18}{sa[k]:>14}{sb[k]:>14}{delta:>+10}")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--responses", help="JSONL of pre-generated responses")
    p.add_argument("--model-cmd", help="Shell command that reads prompt on stdin, prints Lao")
    p.add_argument("--output", help="Write full JSON report here")
    p.add_argument("--compare", nargs=2, metavar=("A", "B"), help="Compare two report files")
    args = p.parse_args()

    if args.compare:
        compare(Path(args.compare[0]), Path(args.compare[1]))
        return

    tests = load_tests()
    responses: dict[str, str] = {}
    if args.responses:
        responses = load_responses(Path(args.responses))
    elif not args.model_cmd:
        p.error("provide --responses, --model-cmd, or --compare")

    graded = []
    for t in tests:
        if args.model_cmd:
            resp = run_model(args.model_cmd, t["prompt"])
        else:
            resp = responses.get(t["id"], "")
        graded.append(grade(t, resp))

    summary = aggregate(graded)
    print_summary(summary, graded)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": summary,
            "results": graded,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nreport -> {out}")

    sys.exit(0 if summary["pass_rate"] == 1.0 else 1)


if __name__ == "__main__":
    main()
