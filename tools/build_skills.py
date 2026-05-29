"""
Build the single skills/khamlao/SKILL.md from data/*.json source files.

Run this whenever data/ changes:
    python tools/build_skills.py

The data/ files stay split by domain for ease of editing, but they are merged
into ONE skill so users see a single `/khamlao` command (no domain picker).

The generated SKILL.md should NOT be edited directly. Edit data/*.json instead.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SKILLS = ROOT / "skills"


# ============ Templates ============

FRONTMATTER = """\
---
name: khamlao
description: |
  ຄຳລາວ (KhamLao) — Lao language quality + compression skill for Claude.
  Always loaded when the user is writing or requesting Lao output.
  Covers: register (ຂ້ອຍ/ເຈົ້າ vs ຂ້າພະເຈົ້າ), tense (ສິ not ຈະ), script-only rules,
  tone marks, top false-friend Thai→Lao corrections, and a built-in vocabulary
  reference (everyday, cooking, school, nature).

  Triggers:
  - "/khamlao" / "/khamlao full" / "ຄຳລາວ" / "ໃຊ້ລາວ" / "ຕອບເປັນລາວ" → enable full
  - "/khamlao lite" → enable lite
  - "/khamlao stop" / "ຢຸດຄຳລາວ" / "ປ່ຽນເປັນປົກກະຕິ" → disable
---
"""

CORE_BODY = """\
# KhamLao (ຄຳລາວ)

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

Most common Claude leaks:

{CRITICAL_TABLE}

For broader vocabulary, see the **Vocabulary reference** section below.

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
"""

VOCAB_HEADER = """\

---

# Vocabulary reference

Thai → Lao (and Lao → English) lookup. Apply the quality rules above to all output.
"""


# ============ Helpers ============

def render_critical_table(critical: list[dict]) -> str:
    lines = ["| Thai (avoid) | Lao (use) | Note |", "|---|---|---|"]
    for e in critical:
        lao = f"`{e['lao']}`"
        if e.get("lao_alt"):
            lao += f" / `{e['lao_alt']}`"
        lines.append(f"| `{e['thai']}` | {lao} | {e['note']} |")
    return "\n".join(lines)


def render_thai_table(entries: list[dict], title: str | None = None) -> str:
    out = []
    if title:
        out.append(f"### {title}")
        out.append("")
    out.append("| Thai | Lao | Note |")
    out.append("|---|---|---|")
    for e in entries:
        out.append(f"| `{e['thai']}` | `{e['lao']}` | {e.get('note', '')} |")
    return "\n".join(out)


def render_lao_table(entries: list[dict], title: str | None = None) -> str:
    out = []
    if title:
        out.append(f"### {title}")
        out.append("")
    out.append("| Lao | English | Note |")
    out.append("|---|---|---|")
    for e in entries:
        out.append(f"| `{e['lao']}` | {e['en']} | {e.get('note', '')} |")
    return "\n".join(out)


# ============ Vocabulary sections ============

def section_everyday() -> tuple[str, int]:
    data = json.loads((DATA / "everyday.json").read_text(encoding="utf-8"))
    parts = ["\n## Everyday (ປະຈຳວັນ)\n",
             "Pronouns, time, family, numbers, common verbs/adjectives, emotions.\n",
             render_thai_table(data["entries"])]
    extras = data.get("extras", {})
    if extras.get("verbs"):
        parts.append("\n" + render_lao_table(extras["verbs"], "Verbs (from MOE textbooks)"))
    if extras.get("objects"):
        parts.append("\n" + render_lao_table(extras["objects"], "Common objects"))
    if extras.get("adjectives"):
        parts.append("\n" + render_lao_table(extras["adjectives"], "Adjectives"))
    total = len(data["entries"]) + sum(len(v) for v in extras.values())
    return "\n".join(parts), total


def section_cooking() -> tuple[str, int]:
    data = json.loads((DATA / "cooking.json").read_text(encoding="utf-8"))
    parts = ["\n## Cooking (ການເຮັດອາຫານ)\n",
             "Ingredients, methods, utensils, tastes, dishes.\n",
             render_thai_table(data["entries"])]
    return "\n".join(parts), len(data["entries"])


def section_school() -> tuple[str, int]:
    data = json.loads((DATA / "school.json").read_text(encoding="utf-8"))
    parts = ["\n## School (ໂຮງຮຽນ)\n",
             "From Lao MOE ປ.1-ປ.4 textbooks.\n",
             render_lao_table(data["entries"])]
    return "\n".join(parts), len(data["entries"])


def section_web() -> tuple[str, int]:
    data = json.loads((DATA / "web.json").read_text(encoding="utf-8"))
    cats = [
        ("auth", "Auth"),
        ("actions", "Actions"),
        ("navigation", "Navigation"),
        ("booking_commerce", "Booking & commerce"),
        ("forms", "Forms"),
        ("status", "Status"),
        ("interface", "Interface"),
    ]
    parts = ["\n## Web / UI (ໜ້າເວັບ ແລະ UI)\n",
             "For building Lao-language interfaces. Entries marked `verify` need "
             "native-speaker confirmation. Loanwords are transliterated (ທັບສັບ).\n"]
    total = 0
    for key, title in cats:
        entries = data.get(key, [])
        if entries:
            parts.append("\n" + render_lao_table(entries, title))
            total += len(entries)
    return "\n".join(parts), total


def section_nature() -> tuple[str, int]:
    data = json.loads((DATA / "nature.json").read_text(encoding="utf-8"))
    parts = ["\n## Nature (ທໍາມະຊາດ)\n", "From Lao MOE ປ.1-ປ.4 textbooks.\n"]
    if data.get("animals"):
        parts.append("\n" + render_lao_table(data["animals"], "Animals (ສັດ)"))
    if data.get("body_parts"):
        parts.append("\n" + render_lao_table(data["body_parts"], "Body parts (ສ່ວນຮ່າງກາຍ)"))
    if data.get("nature"):
        parts.append("\n" + render_lao_table(data["nature"], "Nature (ທໍາມະຊາດ)"))
    total = sum(len(v) for v in data.values() if isinstance(v, list))
    return "\n".join(parts), total


# ============ Build ============

def main() -> None:
    print("Building single KhamLao skill from data/*.json...\n")

    critical = json.loads((DATA / "critical_fixes.json").read_text(encoding="utf-8"))
    body = CORE_BODY.format(CRITICAL_TABLE=render_critical_table(critical["entries"]))

    sections, counts = [], {"critical": len(critical["entries"])}
    for name, fn in (("everyday", section_everyday), ("cooking", section_cooking),
                     ("school", section_school), ("nature", section_nature),
                     ("web", section_web)):
        text, n = fn()
        sections.append(text)
        counts[name] = n

    out = FRONTMATTER + "\n" + body + VOCAB_HEADER + "\n" + "\n".join(sections) + "\n"
    target = SKILLS / "khamlao" / "SKILL.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(out, encoding="utf-8")

    total = sum(counts.values())
    print(f"  skills/khamlao/SKILL.md: {target.stat().st_size:>6} bytes")
    for k, v in counts.items():
        print(f"    {k:10} {v:>4} entries")
    print(f"    {'TOTAL':10} {total:>4} entries")
    print("\nDone. Single skill — users see only /khamlao.")


if __name__ == "__main__":
    main()
