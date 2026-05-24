# KhamLao (ຄຳລາວ)

**Modular Lao language skill for Claude.**

KhamLao makes Claude write authentic, concise Lao instead of slow Thai-influenced verbose text. It cuts ~40-60% of output tokens while enforcing correct Lao register, script, and idiom.

Inspired by [pordee](https://github.com/kerlos/pordee) (Thai compression skill), KhamLao adds Lao-specific quality rules on top of compression.

---

## v1.0 — Modular architecture

KhamLao is split into 5 skills. The **core** is always active when writing Lao; **4 domain glossaries** auto-load by context to keep memory usage low.

```
khamlao                  Core: rules + critical false-friends         (~5 KB, always on)
├─ khamlao-everyday      Time, family, numbers, common verbs/adj      (~9 KB, daily chat)
├─ khamlao-cooking       Food, herbs, methods, utensils, dishes       (~6 KB, food context)
├─ khamlao-school        Education vocabulary                          (~1 KB, school context)
└─ khamlao-nature        Animals, body parts, nature                   (~2 KB, animal/nature context)
```

**Total vocabulary: 314 entries** across rules + 4 domains, sourced from:
- Gemini CLI bootstrap (verified Lao output)
- Native-speaker reviewer (@nouvath07)
- Lao MOE primary school textbooks (ປ.1, ປ.2, ປ.4)

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

This installs all 5 skills (core + 4 domains) to your universal agents directory.

### Manual

Copy `skills/*` to your `~/.claude/skills/`.

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

## How auto-loading works

The **core** skill (`khamlao`) is always loaded when Lao output is requested. It contains:
- 7 quality rules (script, register, tense, tone, no Thai-isms, transliteration, technical IDs)
- 9 critical false-friends (most common Claude leaks)
- Compression rules

The **domain glossaries** load only when relevant:
- Ask about cooking → `khamlao-cooking` auto-loads
- Ask about school → `khamlao-school` auto-loads
- Talk about animals → `khamlao-nature` auto-loads
- General conversation → `khamlao-everyday` auto-loads

This keeps the always-loaded footprint small (~5 KB) while making the full vocabulary (~25 KB) available when needed.

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
│   ├── khamlao/SKILL.md
│   ├── khamlao-everyday/SKILL.md
│   ├── khamlao-cooking/SKILL.md
│   ├── khamlao-school/SKILL.md
│   └── khamlao-nature/SKILL.md
├── tools/
│   ├── build_skills.py      ← Generate SKILL.md from data/
│   └── archive/             ← Historical one-off scripts
├── .claude-plugin/          ← Plugin metadata
├── .github/                 ← Issue & PR templates
├── README.md, CONTRIBUTING.md, LICENSE
```

### To add or fix vocabulary

1. Edit the relevant `data/*.json` file
2. Run `python tools/build_skills.py`
3. Commit both the `data/` change and the regenerated `skills/*/SKILL.md`

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

## Known limitations

- Claude's Lao training data is significantly weaker than English/Thai/Chinese. Domain glossaries help but the skill works best paired with Gemini CLI (which has stronger native Lao).
- Skill auto-loading by context is heuristic — sometimes a domain glossary won't load when you expect it. Use the `/khamlao` trigger to force the core skill.
- Vocabulary is targeted at Vientiane standard Lao. Regional variants (Luang Prabang, Champasak) can be added via contribution.

---

## License

MIT
