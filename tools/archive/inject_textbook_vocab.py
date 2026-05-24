"""Inject the textbook-derived vocab into SKILL.md as Domain glossaries section."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "khamlao" / "SKILL.md"
VOCAB = ROOT / "tools" / "textbook_vocab.json"

CATEGORY_TITLES = {
    "animals": "Animals (ສັດ)",
    "body_parts": "Body parts (ສ່ວນຮ່າງກາຍ)",
    "nature": "Nature (ທໍາມະຊາດ)",
    "school": "School (ໂຮງຮຽນ)",
    "verbs": "Verbs",
    "objects_misc": "Objects (miscellaneous)",
    "adjectives": "Adjectives",
}

data = json.loads(VOCAB.read_text(encoding="utf-8"))
meta = data["_meta"]

lines = []
lines.append("### 5b. Domain glossaries (from Lao MOE primary school textbooks)")
lines.append("")
lines.append(f"Source: Lao MOE textbooks ({', '.join(meta['books_extracted'])}). "
             "Sourced from native-speaker educators — Lao-authoritative. "
             "English glosses are best-effort; corrections welcome via PR.")
lines.append("")

for key, title in CATEGORY_TITLES.items():
    entries = data.get(key, [])
    if not entries:
        continue
    lines.append(f"#### {title}")
    lines.append("")
    lines.append("| Lao | English | Note |")
    lines.append("|---|---|---|")
    for e in entries:
        note = e.get("note", "")
        lines.append(f"| `{e['lao']}` | {e['en']} | {note} |")
    lines.append("")

new_section = "\n".join(lines) + "\n"

skill = SKILL.read_text(encoding="utf-8")
anchor = "### 6. Foreign words"
i = skill.find(anchor)
assert i > 0, "anchor not found"
new_skill = skill[:i] + new_section + skill[i:]
SKILL.write_text(new_skill, encoding="utf-8")

print(f"Old size: {len(skill)} chars")
print(f"New size: {len(new_skill)} chars (+{len(new_skill)-len(skill)})")
print(f"Added {sum(len(data[k]) for k in CATEGORY_TITLES)} entries across {len(CATEGORY_TITLES)} domains")
