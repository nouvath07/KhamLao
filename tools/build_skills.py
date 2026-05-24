"""
Build all skills/*/SKILL.md files from data/*.json source files.

Run this whenever data/ changes:
    python tools/build_skills.py

Generated SKILL.md files should NOT be edited directly. Edit data/*.json instead.
"""
import json
import sys
from pathlib import Path
from textwrap import dedent

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SKILLS = ROOT / "skills"


# ============ Templates ============

CORE_FRONTMATTER = """\
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
"""

CORE_BODY = """\
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

{CRITICAL_TABLE}

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
"""

DOMAIN_FRONTMATTER = """\
---
name: {skill_name}
description: |
  ຄຳລາວ ({domain_lao}) — {description}
  Auto-loads when conversation context involves {context_keywords}.
  Companion to the core `khamlao` skill (which provides rules and critical fixes).

  This skill provides vocabulary lookup only. Quality rules come from `khamlao` core.
---
"""


# ============ Helpers ============

def render_critical_table(critical: list[dict]) -> str:
    """Render the critical false-friends table for the core skill."""
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
        note = e.get("note", "")
        out.append(f"| `{e['thai']}` | `{e['lao']}` | {note} |")
    return "\n".join(out)


def render_lao_table(entries: list[dict], title: str | None = None) -> str:
    out = []
    if title:
        out.append(f"### {title}")
        out.append("")
    out.append("| Lao | English | Note |")
    out.append("|---|---|---|")
    for e in entries:
        note = e.get("note", "")
        out.append(f"| `{e['lao']}` | {e['en']} | {note} |")
    return "\n".join(out)


# ============ Builders ============

def build_core() -> None:
    critical = json.loads((DATA / "critical_fixes.json").read_text(encoding="utf-8"))
    table = render_critical_table(critical["entries"])
    body = CORE_BODY.format(CRITICAL_TABLE=table)
    out = CORE_FRONTMATTER + "\n" + body
    target = SKILLS / "khamlao" / "SKILL.md"
    target.write_text(out, encoding="utf-8")
    print(f"  khamlao (core):           {target.stat().st_size:>6} bytes, {len(critical['entries'])} critical fixes")


def build_everyday() -> None:
    data = json.loads((DATA / "everyday.json").read_text(encoding="utf-8"))
    skill_name = "khamlao-everyday"
    fm = DOMAIN_FRONTMATTER.format(
        skill_name=skill_name,
        domain_lao="ປະຈຳວັນ",
        description="everyday Lao vocabulary (pronouns, time, numbers, family, common verbs/adjectives, emotions)",
        context_keywords="daily conversation, greetings, time, family, numbers, common emotions",
    )
    parts = [fm, ""]
    parts.append("# KhamLao Everyday Vocabulary\n")
    parts.append("Thai → Lao translation reference. Used by the core `khamlao` skill.\n")
    parts.append("## Primary entries\n")
    parts.append(render_thai_table(data["entries"]))
    parts.append("")
    extras = data.get("extras", {})
    if extras.get("verbs"):
        parts.append(f"\n## Additional verbs (from MOE textbooks)\n")
        parts.append(render_lao_table(extras["verbs"]))
        parts.append("")
    if extras.get("objects"):
        parts.append(f"\n## Common objects (from MOE textbooks)\n")
        parts.append(render_lao_table(extras["objects"]))
        parts.append("")
    if extras.get("adjectives"):
        parts.append(f"\n## Additional adjectives (from MOE textbooks)\n")
        parts.append(render_lao_table(extras["adjectives"]))
        parts.append("")
    out = "\n".join(parts)
    target = SKILLS / skill_name / "SKILL.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(out, encoding="utf-8")
    total = len(data["entries"]) + sum(len(v) for v in extras.values())
    print(f"  {skill_name}: {target.stat().st_size:>6} bytes, {total} entries")


def build_cooking() -> None:
    data = json.loads((DATA / "cooking.json").read_text(encoding="utf-8"))
    skill_name = "khamlao-cooking"
    fm = DOMAIN_FRONTMATTER.format(
        skill_name=skill_name,
        domain_lao="ການເຮັດອາຫານ",
        description="Lao cooking and food vocabulary (ingredients, cooking methods, utensils, tastes, common dishes)",
        context_keywords="cooking, recipes, food, ingredients, kitchen, restaurants, dishes",
    )
    parts = [fm, ""]
    parts.append("# KhamLao Cooking Vocabulary\n")
    parts.append("Thai → Lao food/cooking reference. Used by the core `khamlao` skill.\n")
    parts.append(render_thai_table(data["entries"]))
    parts.append("")
    out = "\n".join(parts)
    target = SKILLS / skill_name / "SKILL.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(out, encoding="utf-8")
    print(f"  {skill_name}:  {target.stat().st_size:>6} bytes, {len(data['entries'])} entries")


def build_school() -> None:
    data = json.loads((DATA / "school.json").read_text(encoding="utf-8"))
    skill_name = "khamlao-school"
    fm = DOMAIN_FRONTMATTER.format(
        skill_name=skill_name,
        domain_lao="ໂຮງຮຽນ",
        description="Lao education/school vocabulary from MOE primary textbooks",
        context_keywords="school, education, teaching, learning, students, classroom",
    )
    parts = [fm, ""]
    parts.append("# KhamLao School Vocabulary\n")
    parts.append("From Lao MOE ປ.1-ປ.4 textbooks. Used by the core `khamlao` skill.\n")
    parts.append(render_lao_table(data["entries"]))
    parts.append("")
    out = "\n".join(parts)
    target = SKILLS / skill_name / "SKILL.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(out, encoding="utf-8")
    print(f"  {skill_name}:   {target.stat().st_size:>6} bytes, {len(data['entries'])} entries")


def build_nature() -> None:
    data = json.loads((DATA / "nature.json").read_text(encoding="utf-8"))
    skill_name = "khamlao-nature"
    fm = DOMAIN_FRONTMATTER.format(
        skill_name=skill_name,
        domain_lao="ທໍາມະຊາດ",
        description="Lao animals, body parts, and nature vocabulary from MOE textbooks",
        context_keywords="animals, body parts, nature, environment, forests, weather",
    )
    parts = [fm, ""]
    parts.append("# KhamLao Nature Vocabulary\n")
    parts.append("From Lao MOE ປ.1-ປ.4 textbooks. Used by the core `khamlao` skill.\n")
    if data.get("animals"):
        parts.append("\n## Animals (ສັດ)\n")
        parts.append(render_lao_table(data["animals"]))
        parts.append("")
    if data.get("body_parts"):
        parts.append("\n## Body parts (ສ່ວນຮ່າງກາຍ)\n")
        parts.append(render_lao_table(data["body_parts"]))
        parts.append("")
    if data.get("nature"):
        parts.append("\n## Nature (ທໍາມະຊາດ)\n")
        parts.append(render_lao_table(data["nature"]))
        parts.append("")
    out = "\n".join(parts)
    target = SKILLS / skill_name / "SKILL.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(out, encoding="utf-8")
    total = sum(len(v) for v in data.values() if isinstance(v, list))
    print(f"  {skill_name}:   {target.stat().st_size:>6} bytes, {total} entries")


def main() -> None:
    print("Building KhamLao skill files from data/*.json...\n")
    build_core()
    build_everyday()
    build_cooking()
    build_school()
    build_nature()
    print("\nDone.")


if __name__ == "__main__":
    main()
