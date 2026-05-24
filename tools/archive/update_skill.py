"""Inject the expanded vocab table into skills/khamlao/SKILL.md."""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "khamlao" / "SKILL.md"
VOCAB_TABLE = ROOT / "tools" / "vocab_table.md"

vocab_md = VOCAB_TABLE.read_text(encoding="utf-8")
# Strip the leading comment line from format_vocab.py
vocab_body = "\n".join(line for line in vocab_md.splitlines() if not line.startswith("<!--"))

new_section = f"""### 5. Vocabulary reference (Thai → Lao)

Bootstrapped via Gemini CLI on 2026-05-23 (226 entries). Community corrections welcomed — open an issue or PR if you spot errors.

**Critical false-friends** (most common Claude leaks):

| Thai (avoid) | Lao (use) | Note |
|---|---|---|
| `จะ` (future) | `ສິ` | Most common Claude leak — Thai future marker leaks into Lao |
| `ครับ` / `ค่ະ` | `ໂດຍ` / `ເຈົ້າ` (or drop) | Politeness particles — register dependent |
| `ใคร` | `ໃຜ` | |
| `ที่ไหน` | `ໃສ` | |
| `อะไร` | `ຫຍັງ` | |
| `ขอบคุณ` | `ຂອບໃຈ` | |
| `ไม่` | `ບໍ່` | |
| `ทำ` | `ເຮັດ` | |
| `เป็น` (identity) | `ແມ່ນ` | |
| `เท่าไหร่` | `ເທົ່າໃດ` / `ທໍ່ໃດ` | |

**Extended vocabulary**

{vocab_body.strip()}

"""

skill = SKILL.read_text(encoding="utf-8")
anchor = "### 5. No Thai-isms"
end_anchor = "### 6. Foreign words"
i = skill.find(anchor)
j = skill.find(end_anchor)
assert i > 0 and j > i, f"anchors not found: i={i}, j={j}"

new_skill = skill[:i] + new_section + skill[j:]
SKILL.write_text(new_skill, encoding="utf-8")
print(f"old size: {len(skill)} chars")
print(f"new size: {len(new_skill)} chars")
print(f"delta: +{len(new_skill) - len(skill)} chars")
