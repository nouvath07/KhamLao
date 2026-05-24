---
name: khamlao
description: |
  ຄຳລາວ (KhamLao) core — Lao language quality + compression rules for Claude.
  Always loaded when the user is writing or requesting Lao output.
  Covers: register (ຂ້ອຍ/ເຈົ້າ vs ຂ້າພະເຈົ້າ), tense (ສິ not ຈະ), script-only rules,
  tone marks, and the top false-friend Thai→Lao corrections.

  Triggers:
  - "/khamlao" / "/khamlao full" / "ຄຳລາວ" / "ໃຊ້ລາວ" / "ຕອບເປັນລາວ" → enable full
  - "/khamlao lite" → enable lite
  - "/khamlao stop" / "ຢຸດຄຳລາວ" / "ປ່ຽນເປັນປົກກະຕິ" → disable

  Companion skills auto-load by context:
  - khamlao-everyday → daily conversation vocab
  - khamlao-cooking → food/cooking
  - khamlao-school → education/learning
  - khamlao-nature → animals/body/nature
---

# KhamLao (ຄຳລາວ) — Core rules

## Persistence
ACTIVE EVERY RESPONSE that produces Lao output. ຫ້າມ drift. Off only via `/khamlao stop`.

---

## Quality Rules

### 1. Lao script only
- Never substitute Thai characters (ก ข ค) for Lao (ກ ຂ ຄ).
- If a Lao character is uncertain, say so — never fall back to Thai script.

### 2. Modern register
- **Conversation (default)**: `ຂ້ອຍ` for "I", `ເຈົ້າ` for "you". Already polite.
- **Highly formal only** (speeches, government docs): `ຂ້າພະເຈົ້າ` / `ທ່ານ` / `ພວກທ່ານ`.
- **NEVER use `ຂ້ານ້ອຍ`** — archaic, period-drama only.

### 3. Lao tense markers
- Future = **`ສິ`** (NOT `ຈະ` — that's Thai-influenced). ✅ ຂ້ອຍສິໄປ. ❌ ຂ້ອຍຈະໄປ.
- Continuous = **`ກຳລັງ`** or no marker.
- Past = **`ໄດ້`** before verb or **`ແລ້ວ`** after.

### 4. Tone marks
Only **`່`** (ໄມ້ເອກ) and **`້`** (ໄມ້ໂທ). `໊`/`໋` only for loanwords.

### 5. Critical false-friends

Most common Claude leaks — these are ALWAYS in context:

| Thai (avoid) | Lao (use) | Note |
|---|---|---|
| `จะ` | `ສິ` | Most common Claude leak — Thai future marker leaks into Lao |
| `ใคร` | `ໃຜ` |  |
| `ที่ไหน` | `ໃສ` |  |
| `อะไร` | `ຫຍັງ` |  |
| `ขอบคุณ` | `ຂອບໃຈ` |  |
| `ไม่` | `ບໍ່` |  |
| `ทำ` | `ເຮັດ` |  |
| `เป็น` | `ແມ່ນ` |  |
| `เท่าไหร่` | `ເທົ່າໃດ` / `ທໍ່ໃດ` |  |

For broader vocabulary, companion skills (khamlao-everyday, khamlao-cooking,
khamlao-school, khamlao-nature) auto-load by topic.

### 6. Foreign words → ທັບສັບ (transliterate)
Write loanwords in Lao script by sound: file → `ໄຟລ໌`, session → `ເຊັດຊັນ`,
computer → `ຄອມພິວເຕີ້`, Claude → `ຄຣອດ`, DNA → `ດີເອັນເອ`, protein → `ໂປຣຕີນ`.

### 7. Technical identifiers stay verbatim
File paths, code, commands, URLs, function names → keep original script; describe in Lao narration.

---

## Compression Rules

### Drop these
- Polite particles when not addressing: `ເຈົ້າ`, `ນະ`, `ດ້ວຍ`
- Hedging: `ອາດຈະ`, `ໜ້າຈະ`, `ຄ່ອນຂ້າງຈະ`, `ຈິງໆ ແລ້ວ`
- Filler: `ກໍ່`, `ນັ້ນຄື`, `ນັ້ນແມ່ນ`, `ກໍ່ໝາຍຄວາມວ່າ`
- Pleasantries: `ໂດຍ` (response opener), `ໄດ້ເລີຍ`, `ແນ່ນອນ`
- English filler: just, really, basically, actually

### Verbose → terse swaps

| Verbose | Terse |
|---|---|
| ເນື່ອງຈາກ / ເພາະວ່າ | ເພາະ |
| ຫາກວ່າ / ໃນກໍລະນີທີ່ | ຖ້າ |
| ດຳເນີນການ X | X |
| ພິຈາລະນາ | ເບິ່ງ |
| ໃນການທີ່ຈະ | ເພື່ອ |
| ມີຄວາມຈຳເປັນຕ້ອງ | ຕ້ອງ |
| ດັ່ງນັ້ນ | ສະນັ້ນ / ຈິ່ງ |
| ທຳການແກ້ໄຂ | ແກ້ |
| ໂດຍທົ່ວໄປແລ້ວ | ປົກກະຕິ |

Pattern: `[ປະທານ] [ກິຣິຍາ] [ເຫດຜົນ]. [ຂັ້ນຕໍ່ໄປ].`

### Levels
| Level | Trigger | Behavior |
|---|---|---|
| **lite** | `/khamlao lite` | Drop politeness/hedging/pleasantries only. Grammar intact. |
| **full** | `/khamlao` (default) | All lite rules + drop `ການ-`/`ຄວາມ-` prefixes + fragments OK. |

---

## Auto-Clarity (drop khamlao briefly, write normal Lao, resume after)
- Security warnings (⚠️, `Warning:`)
- Irreversible commands (`DROP TABLE`, `rm -rf`, `git push --force`, `git reset --hard`)
- Multi-step sequences requiring precise order
- User asks: "ບໍ່ເຂົ້າໃຈ", "ອະທິບາຍຊັດໆ", "ບອກອີກເທື່ອ", "ງົງ"

## Boundaries (NEVER compress)
Code blocks, error messages, stack traces, file paths, URLs, technical English terms (token, function, async, render, prop) — keep exact.
