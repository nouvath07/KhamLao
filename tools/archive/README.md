# Archive — one-off scripts and artifacts from v0.1 → v0.4

These scripts and data files were used during the iterative bootstrap of the
KhamLao vocabulary (v0.1 → v0.4). They are kept here for historical reference
and are NOT part of the v1.0 build pipeline.

## Scripts

- `bootstrap_vocab.py` — Original batched Gemini caller (10 words at a time). v0.2 era.
- `bootstrap_one_shot.py` — Single-shot Gemini caller, used for cooking attempt (failed on quota).
- `format_vocab.py` — Converted Gemini TSV → markdown tables. Superseded by `build_skills.py`.
- `update_skill.py` — Injected vocab tables into SKILL.md. Superseded by `build_skills.py`.
- `inject_textbook_vocab.py` — Added MOE textbook glossaries. Superseded by data/ + build_skills.py.
- `migrate_v1.py` — One-time migration: monolithic SKILL.md → modular data/*.json.

## Data artifacts

- `seed_words.json` — Original Thai seed words sent to Gemini. Now obsolete; data lives in data/*.json.
- `vocab_raw.json` — Gemini raw output. Kept as provenance for v0.2 entries.
- `vocab_general.tsv` — Intermediate TSV from Gemini.
- `vocab_table.md` — Intermediate generated table.
- `textbook_vocab.json` — Original MOE textbook extraction. Now in data/nature.json + data/school.json + etc.

## v1.0+ active pipeline

The active build pipeline is:

```
data/*.json  →  tools/build_skills.py  →  skills/*/SKILL.md
```

Edit `data/*.json` to add or fix vocabulary, then run `python tools/build_skills.py`.
