# KhamLao (ຄຳລາວ)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Built for Claude](https://img.shields.io/badge/built%20for-Claude-orange)](https://www.anthropic.com/claude-code)
[![Lao language](https://img.shields.io/badge/language-ລາວ-success)](https://en.wikipedia.org/wiki/Lao_language)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Modular Lao language skill for Claude.**

KhamLao makes Claude write authentic, concise Lao instead of slow Thai-influenced verbose text. It cuts ~40-60% of output tokens while enforcing correct Lao register, script, and idiom.

Inspired by [pordee](https://github.com/kerlos/pordee) (Thai compression skill), KhamLao adds Lao-specific quality rules on top of compression.

---

## Architecture — one skill, one command

KhamLao is a **single skill** (`/khamlao`). The data is kept split by domain in
`data/*.json` for ease of editing, but `build_skills.py` merges everything into
one `SKILL.md` — so users see just one command, never a domain picker.

```
skills/khamlao/SKILL.md   (~26 KB)
├─ Quality rules + critical false-friends   (always)
└─ Vocabulary reference
   ├─ Everyday   time, family, numbers, common verbs/adj
   ├─ Cooking    food, herbs, methods, utensils, dishes
   ├─ School     education vocabulary
   ├─ Nature     animals, body parts, nature
   └─ Web / UI   auth, actions, nav, booking, forms, status
```

**Total vocabulary: 390 entries**, sourced from:
- Gemini CLI bootstrap (verified Lao output)
- Native-speaker reviewer (@nouvath07)
- Lao MOE primary school textbooks (ປ.1, ປ.2, ປ.4)
- Web/UI terms for building Lao-language interfaces (entries marked `verify` pending native review)

> **Note on scale:** the whole vocabulary loads into context with the skill.
> That's fine at this size; once it grows past ~1–2K entries the plan is to move
> the long tail to a lookup tool (see "What's next").

---

## Install

### Via Claude Code plugin marketplace

```bash
claude plugin marketplace add nouvath07/khamlao
claude plugin install khamlao@khamlao
```

### Via `npx skills add`

```bash
npx skills add https://github.com/nouvath07/KhamLao --skill khamlao
```

This installs the single `khamlao` skill to your universal agents directory.

### Manual

Copy `skills/khamlao/` to your `~/.claude/skills/`.

---

## Usage

### Slash commands

| Command | Effect |
|---|---|
| `/khamlao` | Enable full mode (default) |
| `/khamlao full` | Enable full mode explicitly |
| `/khamlao lite` | Enable lite mode (gentler compression) |
| `/khamlao stop` | Disable |

### Lao keyword triggers (no slash needed)

| Keyword | Effect |
|---|---|
| `ຄຳລາວ` | Enable |
| `ໃຊ້ລາວ` | Enable |
| `ຕອບເປັນລາວ` | Enable |
| `ຢຸດຄຳລາວ` | Disable |
| `ປ່ຽນເປັນປົກກະຕິ` | Disable |

---

## How it loads

The single `khamlao` skill loads when Lao output is requested. It contains:
- 7 quality rules (script, register, tense, tone, no Thai-isms, transliteration, technical IDs)
- 9 critical false-friends (most common Claude leaks)
- Compression rules
- The full vocabulary reference (everyday, cooking, school, nature)

One skill, one command — no domain picker. The whole skill (~21 KB) loads
together. Most response latency for Lao comes from generating Lao output tokens
(Lao tokenizes to ~5–10× English), not from this context, so a single merged
skill keeps the UX simple without a meaningful speed cost at the current size.

---

## Quality

### Quality rules (always when writing Lao)

- **Lao script only** — never substitutes Thai characters
- **Modern register** — `ຂ້ອຍ`/`ເຈົ້າ` for conversation; never archaic `ຂ້ານ້ອຍ`
- **Correct tense** — `ສິ` for future (not Thai-influenced `ຈະ`)
- **Lao tone marks only** — `່` and `້`
- **No Thai-isms** — `ໃຜ` not `ใคร`, `ໃສ` not `ที่ไหน`, `ບໍ່` not `ไม่`
- **Foreign words → ທັບສັບ** — `ໄຟລ໌`, `ເຊັດຊັນ`, `ຄອມພິວເຕີ້`

### Compression (token savings)

- Drops politeness particles, hedging, fillers, pleasantries
- Verbose → terse swaps (e.g., `ເນື່ອງຈາກ` → `ເພາະ`)
- Two levels: `lite` (gentle) and `full` (aggressive)

### Safety boundaries (NEVER compressed)

- Code blocks, error messages, stack traces — verbatim
- File paths, URLs, identifiers — verbatim
- Security warnings, irreversible commands — written in clear standard Lao

---

## Repo structure

```
khamlao/
├── data/                    ← Source-of-truth (edit here)
│   ├── critical_fixes.json
│   ├── everyday.json
│   ├── cooking.json
│   ├── school.json
│   └── nature.json
├── skills/                  ← Generated (do not edit directly)
│   └── khamlao/SKILL.md     ← Single merged skill (all domains)
├── tools/
│   ├── build_skills.py      ← Merge data/*.json into the single SKILL.md
│   ├── khamlao_checker.py   ← Quality detector (Thai-leak, register, tone)
│   ├── scrape_lao_corpus.py ← Corpus pipeline (PDF → OCR → JSONL)
│   └── archive/             ← Historical one-off scripts
├── .claude-plugin/          ← Plugin metadata
├── .github/                 ← Issue & PR templates
├── README.md, CONTRIBUTING.md, LICENSE
```

### To add or fix vocabulary

1. Edit the relevant `data/*.json` file
2. Run `python tools/build_skills.py`
3. Commit both the `data/` change and the regenerated `skills/khamlao/SKILL.md`

---

## Contributing

KhamLao is community-driven. **Native and fluent Lao speakers — your help is essential.**

- 🐛 **Report Thai-influenced output** — when Claude leaks Thai vocabulary/script
- 📚 **Add vocabulary** — Thai → Lao mappings the current rules miss
- 🌾 **Add domain glossaries** — propose new domains beyond the current 4
- 📝 **Fix register/tone errors**

See [CONTRIBUTING.md](CONTRIBUTING.md). You don't need to be a programmer — language data is most valuable.

---

## For developers/contributors

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — how the system works, data flow, schemas, build process
- **[ROADMAP.md](ROADMAP.md)** — open tasks organized by impact and difficulty
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — how to submit changes

---

## What's next

KhamLao today is a **prompt-injected skill** — it corrects Claude/Gemini's Lao output at generation time. The next step is to make those same rules usable **outside** an LLM, as a standalone quality layer for any Lao NLP system:

### 🔬 Quality / correctness layer (in design)

A Python library + eval suite that any Lao OCR, TTS, or translation pipeline can call to check its own output. Three components:

```
┌─────────────────────────────────────────────┐
│  Layer 3: Eval suite (benchmark runner)     │  → measure model output quality
├─────────────────────────────────────────────┤
│  Layer 2: Detector library (Python pkg)     │  → Thai-leak + register checks
├─────────────────────────────────────────────┤
│  Layer 1: Rules + test data (JSON)          │  → already 80% in data/*.json
└─────────────────────────────────────────────┘
```

**Detector example:**
```python
from khamlao_checker import check
check("ຂ້ອຍຈະໄປເຮັດວຽກ")
# → {"thai_word_leaks": ["ຈະ"], "suggested": "ສິ",
#    "register": "modern", "score": 0.72}
```

**Why it matters:** ML teams optimize average accuracy, but no one currently checks whether Lao output is *actually good Lao* — free of Thai-script leaks, archaic pronouns, or wrong tense markers. That gap is what KhamLao's rules already encode for LLMs; the next step is exposing them as a reusable checker.

### 📚 Corpus pipeline (shipped, v1.1)

`tools/scrape_lao_corpus.py` — download → render → Gemini OCR → quality-filter → JSONL. Used to harvest Lao text from MOE textbooks (ປ.1–ມ.7) for training and evaluation. See [data/corpora/README.md](data/corpora/README.md).

### 🛣 Roadmap details

See [ROADMAP.md](ROADMAP.md) — 6 themes, prioritized, with effort estimates. Contributors welcome at any tier of complexity.

---

## Known limitations

- Claude's Lao training data is significantly weaker than English/Thai/Chinese. Domain glossaries help but the skill works best paired with Gemini CLI (which has stronger native Lao).
- Skill auto-loading by context is heuristic — sometimes a domain glossary won't load when you expect it. Use the `/khamlao` trigger to force the core skill.
- Vocabulary is targeted at Vientiane standard Lao. Regional variants (Luang Prabang, Champasak) can be added via contribution.

---

## License

MIT
