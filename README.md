# KhamLao (ຄຳລາວ)

**Lao language quality + compression mode for Claude.**

KhamLao makes Claude write authentic, concise Lao instead of slow Thai-influenced verbose text. It cuts ~40-60% of output tokens while enforcing correct Lao register, script, and idiom.

Inspired by [pordee](https://github.com/kerlos/pordee) (Thai compression skill), KhamLao adds **Lao-specific quality rules** on top of compression, because Claude's Lao output often suffers from two compounding issues:

1. **Slow generation** — Lao tokenizes to ~5-10× more tokens than English (UTF-8 3 bytes/char + combining marks + low-resource tokenizer)
2. **Thai-influenced or archaic Lao** — wrong tense markers (ຈະ instead of ສິ), outdated pronouns (ຂ້ານ້ອຍ), Thai vocabulary leaking in

KhamLao fixes both.

---

## Install

### Via Claude Code plugin marketplace

```bash
claude plugin marketplace add nouvath07/khamlao
claude plugin install khamlao@khamlao
```

### Via `npx skills add`

```bash
npx skills add https://github.com/nouvath07/khamlao --skill khamlao
```

### Manual

Copy `skills/khamlao/SKILL.md` to `~/.claude/skills/khamlao/SKILL.md`.

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

## What KhamLao does

### Quality (always when writing Lao)

- **Lao script only** — never substitutes Thai characters
- **Modern register** — `ຂ້ອຍ`/`ເຈົ້າ` for conversation; never archaic `ຂ້ານ້ອຍ`
- **Correct tense** — `ສິ` for future (not Thai-influenced `ຈະ`)
- **Lao tone marks only** — `່` and `້` (no `໊`/`໋` in native Lao)
- **No Thai-isms** — `ໃຜ` not `ใคร`, `ໃສ` not `ที่ไหน`, `ບໍ່` not `ไม่`
- **Foreign words → ທັບສັບ** (transliteration) — `ໄຟລ໌`, `ເຊັດຊັນ`, `ຄອມພິວເຕີ້`

### Compression (token savings)

- Drops politeness particles, hedging, fillers, pleasantries
- Verbose → terse swaps (e.g., `ເນື່ອງຈາກ` → `ເພາະ`)
- Two levels: `lite` (gentle) and `full` (aggressive)
- Allows sentence fragments in `full` mode

### Safety boundaries (NEVER compressed)

- Code blocks, error messages, stack traces — verbatim
- File paths, URLs, identifiers — verbatim
- Security warnings, irreversible commands — written in clear standard Lao
- Multi-step sequences requiring order — written clearly

---

## Example token savings

### Tech question

**Q**: "ເປັນຫຍັງ React component ຈິ່ງ re-render?"

| Mode | Tokens | Response |
|---|---|---|
| normal | ~75 | (verbose with politeness, hedging, full sentences) |
| khamlao lite | ~38 | "React component re-render ເພາະສົ່ງ object ref ໃໝ່ເປັນ prop ທຸກຄັ້ງທີ່ render. ລອງໃຊ້ useMemo." |
| khamlao full | ~16 | "Object ref ໃໝ່ທຸກ render. Inline prop = ref ໃໝ່ = re-render. ຫໍ້ດ້ວຍ `useMemo`." |

**Savings: ~78% in full mode**

### Daily question

**Q**: "ໄປຈຳປາສັກເດືອນໃດດີ?"

| Mode | Tokens |
|---|---|
| normal | ~70 |
| khamlao full | ~10 |

**Savings: ~86%**

---

## Comparison with pordee

| | pordee | KhamLao |
|---|---|---|
| Language | Thai | Lao |
| Compression | ✅ | ✅ |
| Quality rules (script, register) | ❌ | ✅ |
| Foreign-word transliteration | ❌ | ✅ |
| Auto-clarity for risky ops | ✅ | ✅ |
| Architecture | Full plugin (hooks + state + stats) | Skill-only (v1) |

KhamLao v1 focuses on the **skill content** — the rules Claude follows. Future versions may add hooks, persistent state, and `/khamlao-stats` like pordee.

---

## Contributing

KhamLao is community-driven. **Native and fluent Lao speakers — your help is essential.** Claude's Lao training is limited, and the skill works best when the community contributes:

- 🐛 **Report Thai-influenced output** — when Claude leaks Thai vocabulary/script into Lao
- 📚 **Add vocabulary** — Thai → Lao mappings the current rules miss
- 🌾 **Add domain glossaries** — cooking, tech, medical, agriculture, etc.
- 📝 **Fix register/tone errors** — improve the rule set

See [CONTRIBUTING.md](CONTRIBUTING.md) for details. You don't need to be a programmer — language data contributions are most valuable.

## Known limitations

- Claude's Lao training data is **significantly weaker** than its English/Thai/Chinese. Even with KhamLao active, output may still leak Thai vocabulary in specialized domains (cooking ingredients, technical terms, regional words).
- The vocabulary table in `SKILL.md` currently covers ~15 common words. Expansion is community-driven via PRs.
- Lao has regional variations; the skill currently targets standard Vientiane Lao. Regional alternatives can be added via contribution.

## License

MIT
