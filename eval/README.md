# `eval/` — KhamLao evaluation suite

Layer 3 of the quality stack: a benchmark that scores any model's Lao output
against a fixed test set, using `tools/khamlao_checker.py` (Layer 2) plus
per-test assertions.

## Files

| File | What it is |
|---|---|
| `test_set.json` | The benchmark: prompts + `expect_contains` / `forbid_contains` assertions |
| `runner.py` | Harness — grades responses, prints summary, writes JSON report |
| `sample_responses.jsonl` | Demo responses (mostly clean, 2 deliberate leaks) so the runner is runnable out of the box |
| `reports/` | Generated reports (gitignored) |

## Quick start

```bash
# Score the bundled sample responses:
python eval/runner.py --responses eval/sample_responses.jsonl

# Save a full JSON report:
python eval/runner.py --responses eval/sample_responses.jsonl --output eval/reports/run.json

# Compare two reports (e.g. before/after a model or data change):
python eval/runner.py --compare eval/reports/baseline.json eval/reports/run.json
```

## Scoring your own model

Two ways to feed responses in:

**1. Offline** — generate responses yourself, one JSONL line per test:
```json
{"id": "trans_001", "response": "ໄປໃສ"}
```
```bash
python eval/runner.py --responses my_model_out.jsonl --output eval/reports/my_model.json
```

**2. Live** — shell out to any CLI that reads a prompt on stdin and prints Lao:
```bash
python eval/runner.py --model-cmd "gemini -p" --output eval/reports/gemini.json
```

## How a test passes

A test passes when **all** hold:
- every string in `expect_contains` is present
- no string in `forbid_contains` is present
- `khamlao_checker` score ≥ 0.8 (no major Thai-leak / archaic / tone issues)
- response is non-empty

## Metrics reported

- **pass_rate** — fraction of tests passing
- **mean_score** — average `khamlao_checker` score across responses
- **thai_leak_rate** — fraction of responses containing any Thai-script character
- **by_category** — same metrics split by test category (translation, register, domain_*, edge_*)

## Extending the test set

Add objects to `tests` in `test_set.json`. Keep each test:
- **atomic** — one phenomenon per test (one false-friend, one register rule)
- **assertion-backed** — prefer `expect_contains` / `forbid_contains` over relying on score alone
- **native-reviewed** — the assertions encode "correct Lao", so they need a fluent speaker's sign-off

Categories currently covered: `translation_th_lo`, `register`, `freeform`,
`domain_cooking`, `domain_school`, `domain_nature`, `edge_loanword`,
`edge_question`. The test set is intentionally small (15) — growing it with
native-speaker-reviewed cases is tracked in `ROADMAP.md` (Theme 4).
