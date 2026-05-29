# KhamLao — System Architecture

A technical walkthrough of how KhamLao works, intended for engineers and developers who want to contribute meaningfully.

---

## What is KhamLao trying to solve?

When LLMs (Claude, Gemini, etc.) write Lao, they produce text with two problems:

1. **Slow generation** — Lao tokenizes to ~5–10× more tokens than English. UTF-8 uses 3 bytes per Lao character (range U+0E80–U+0EFF), and BPE tokenizers fall back to byte-level encoding because Lao is underrepresented in training data. A 100-character Lao response can be 300+ tokens.

2. **Thai-influenced output** — Lao is the second-largest dataset for Lao-Thai bilingual content online, so LLMs tend to:
   - Use Thai vocabulary that "looks Lao" (e.g., `ไหม` instead of `ບໍ`)
   - Use Thai grammar patterns (e.g., `ຈະ` future marker instead of Lao `ສິ`)
   - Use archaic pronouns from old translation data (`ຂ້ານ້ອຍ`)
   - Mix Thai and Lao scripts inadvertently

KhamLao is a **Claude Code Skill** (a prompt-engineering artifact that gets injected into Claude's context) that addresses both problems by:
- Telling the model the correct Lao register, tense markers, tone rules
- Providing a curated vocabulary lookup (Thai→Lao + domain-specific Lao)
- Adding compression rules to drop padding particles

---

## High-level data flow

```
                  ┌─────────────────┐
                  │ data/*.json     │  ← Source-of-truth (edit here)
                  │  - critical_fixes
                  │  - everyday
                  │  - cooking
                  │  - school
                  │  - nature
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ build_skills.py │  ← Generator
                  │  - Reads JSON
                  │  - Templates    │
                  │  - Writes MD    │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ skills/khamlao/  │  ← Generated (don't edit)
                  │   SKILL.md       │  Single merged skill:
                  │  rules + all     │  rules + critical fixes
                  │  vocab domains   │  + everyday/cooking/
                  │                  │    school/nature vocab
                  └────────┬────────┘
                           │
                           │  installed via npx skills add OR plugin install
                           ▼
              ┌──────────────────────────┐
              │ ~/.agents/skills/        │  ← Local install location
              │   (Claude/Gemini/Copilot)│
              └────────┬─────────────────┘
                       │
                       ▼  loaded into context at runtime
              ┌──────────────────────────┐
              │ Claude/Gemini answer Lao │
              │ following skill rules    │
              └──────────────────────────┘
```

---

## How Claude Code Skills work

A "skill" in Claude Code is a directory with a `SKILL.md` file. The file has:

1. **YAML frontmatter** containing:
   - `name`: unique identifier
   - `description`: tells Claude WHEN to load this skill (matched against conversation context)

2. **Markdown body** — the actual instructions, vocabulary tables, examples that get injected into Claude's context when the skill is "active."

### Loading mechanics

When the user sends a message, Claude evaluates each available skill's `description` against the conversation context. A matching skill gets **loaded** (its full body is prepended to Claude's working context).

KhamLao is a single skill: its `description` matches "Lao output requested", so the whole skill — rules, critical fixes, and the full vocabulary reference — loads together (~21 KB). Users see one `/khamlao` command, never a domain picker.

### Single skill vs modular — why we merged

KhamLao briefly used 5 modular skills (v1.0) that auto-loaded by topic, to keep the always-on footprint small. We merged back to one skill (v1.1) because:

- **UX**: 5 skills surfaced as 5 slash commands (`/khamlao`, `/khamlao-cooking`, …), cluttering the command list and implying users had to pick a domain. They never did — domains auto-loaded — but the clutter was confusing.
- **Speed reality**: profiling showed Lao latency is dominated by *output* token generation (Lao tokenizes to ~5–10× English), not by the *input* skill context. Trimming the ~5 KB core to a smaller always-on slice saves only a fraction of a second of prefill, while output generation is unchanged. So the modular split bought little real speed.
- **Maintenance**: one build target, one skill to install and version.

The `data/*.json` files stay split by domain — that boundary is for *editing convenience*, not delivery. `build_skills.py` merges them into the single skill.

**Scaling caveat:** the whole vocabulary now loads into context. Fine at ~390 entries; once vocabulary grows past ~1–2K entries, the plan is to move the long tail to a lookup tool (RAG-style) so context stays small. The single `/khamlao` command stays the same to users either way.

---

## Repo structure

```
khamlao/
├── README.md                ← User-facing intro + install
├── ARCHITECTURE.md          ← This file
├── ROADMAP.md               ← Where we're going + open tasks
├── CONTRIBUTING.md          ← How to submit changes
├── LICENSE                  ← MIT
├── .gitignore
│
├── .claude-plugin/          ← Plugin metadata (for marketplace install)
│   ├── plugin.json          Plugin descriptor
│   └── marketplace.json     Marketplace listing
│
├── .github/                 ← GitHub-specific
│   ├── ISSUE_TEMPLATE/      Issue templates (thai-leak, vocab-addition)
│   └── PULL_REQUEST_TEMPLATE.md
│
├── data/                    ← THE SOURCE OF TRUTH
│   ├── critical_fixes.json  9 false-friends always loaded
│   ├── everyday.json        ~170 entries: pronouns, time, family, common
│   ├── cooking.json         ~90 entries: food, herbs, methods
│   ├── school.json          ~15 entries: education vocab
│   ├── nature.json          ~32 entries: animals, body, nature
│   └── web.json             ~72 entries: UI/web/tech (native-reviewed)
│
├── skills/                  ← GENERATED — do not edit by hand
│   └── khamlao/SKILL.md          Single merged skill: rules + all vocab
│
└── tools/
    ├── build_skills.py      Active: merge data/*.json into the single skill
    ├── khamlao_checker.py   Quality detector (Thai-leak, register, tone)
    ├── scrape_lao_corpus.py Corpus pipeline (PDF → OCR → JSONL)
    └── archive/             Historical one-off scripts (v0.1 → v0.4)
```

---

## Data schemas

### `critical_fixes.json` — Top false-friends

```json
{
  "entries": [
    {
      "thai": "จะ",
      "lao": "ສິ",
      "note": "Future tense marker — most common Claude leak"
    },
    ...
  ]
}
```

### `everyday.json` — General everyday vocab

```json
{
  "entries": [
    { "thai": "ฉัน", "lao": "ຂ້ອຍ", "note": "I" },
    ...
  ],
  "extras": {
    "verbs":      [ { "lao": "ຮຽນ", "en": "to study" }, ... ],
    "objects":    [ ... ],
    "adjectives": [ ... ]
  }
}
```

Note the schema variation: `entries` has `thai`+`lao`+`note` (Thai→Lao mapping), while `extras` has `lao`+`en` (Lao with English gloss). This is because `extras` came from textbook extraction where we don't have a clean Thai equivalent.

### `cooking.json`, `school.json` — same as everyday

### `nature.json` — sub-categorized

```json
{
  "animals":    [ { "lao": "ເສືອ", "en": "tiger" }, ... ],
  "body_parts": [ ... ],
  "nature":     [ ... ]
}
```

---

## The build process (`tools/build_skills.py`)

Single Python file. Run with `python tools/build_skills.py`.

It does:
1. Read all `data/*.json` files
2. Render each into markdown tables (`section_everyday`, `section_cooking`, …)
3. Concatenate core rules + critical fixes + all vocab sections
4. Write the single `skills/khamlao/SKILL.md`

The templates are inlined in the script (no separate template files).

**Adding a new domain** requires:
1. Create `data/<domain>.json` with appropriate schema
2. Add a `section_<domain>()` function in `build_skills.py`
3. Append it to the section list in `main()`
4. Run the build

**This is intentionally simple** — Python stdlib only, no dependencies, easy to read in one sitting.

---

## Local install vs published install

### Local development install

After running `python tools/build_skills.py`, the generated `skills/*/SKILL.md` files are NOT yet visible to Claude Code unless installed:

```bash
# Easiest: install from local path (will copy or symlink)
npx skills add ./khamlao
```

Or manually:

```bash
# Universal location used by Claude Code, Gemini CLI, etc.
cp -r skills/khamlao ~/.agents/skills/

# Claude Code reads from ~/.claude/skills/ too — symlink for convenience
ln -s ~/.agents/skills/khamlao ~/.claude/skills/khamlao
```

### Published install (for end users)

After pushing to GitHub:

```bash
npx skills add https://github.com/nouvath07/KhamLao --skill khamlao
```

This fetches the latest from the main branch.

Or via plugin marketplace:

```bash
claude plugin marketplace add nouvath07/khamlao
claude plugin install khamlao@khamlao
```

---

## Current state of contributions

| Version | Date       | Highlights                                      |
|---------|------------|-------------------------------------------------|
| v0.1    | 2026-05-23 | Initial scaffold; 15 hand-written entries       |
| v0.2    | 2026-05-23 | Gemini-bootstrapped 226 general entries         |
| v0.3    | 2026-05-23 | Native-speaker review: 10 corrections           |
| v0.4    | 2026-05-24 | + 78 entries from Lao MOE primary textbooks     |
| v1.0    | 2026-05-24 | Modular refactor; 5 skills; 318 total entries   |
| v1.1    | 2026-05-29 | Merge back to 1 skill; + quality checker, eval suite, corpus pipeline |

---

## What this skill is NOT

To set scope expectations:

- **NOT a Lao dictionary.** It's a corrective overlay for LLMs. The vocab table fixes Claude's wrong defaults, not provides exhaustive lookup.
- **NOT a translation tool.** It improves quality of LLM-generated Lao but doesn't translate documents.
- **NOT a Lao language tutor.** It's for engineers using Claude/Gemini to write Lao.
- **NOT a finetuned model.** It's a system prompt artifact. Lao quality is fundamentally limited by what Claude/Gemini can do.

The skill works best with **Gemini CLI** (which has stronger native Lao than Claude). For Claude, the skill significantly improves output but won't perfectly match a native speaker.

---

## Key files to read for understanding the codebase

1. `data/critical_fixes.json` — the single most important file (rules everyone needs)
2. `tools/build_skills.py` — see how skills are generated
3. `skills/khamlao/SKILL.md` — read what Claude actually sees
4. This file (`ARCHITECTURE.md`)
5. `ROADMAP.md` — what's next
