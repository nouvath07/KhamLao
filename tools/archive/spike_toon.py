"""
Spike test: convert khamlao-cooking SKILL.md to TOON format and measure tokens.

Generates two files:
- skills/khamlao-cooking/SKILL.md (original — keep)
- skills/khamlao-cooking/SKILL_toon.md (TOON variant for comparison)

Reports token counts side-by-side.
"""
import json
import sys
from pathlib import Path
import tiktoken

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "cooking.json"
SKILL = ROOT / "skills" / "khamlao-cooking" / "SKILL.md"
SKILL_TOON = ROOT / "skills" / "khamlao-cooking" / "SKILL_toon.md"

# Build TOON version
data = json.loads(DATA.read_text(encoding="utf-8"))
entries = data["entries"]

frontmatter = """\
---
name: khamlao-cooking
description: |
  ຄຳລາວ (ການເຮັດອາຫານ) — Lao cooking and food vocabulary (ingredients, cooking methods, utensils, tastes, common dishes)
  Auto-loads when conversation context involves cooking, recipes, food, ingredients, kitchen, restaurants, dishes.
  Companion to the core `khamlao` skill (which provides rules and critical fixes).

  This skill provides vocabulary lookup only. Quality rules come from `khamlao` core.
---

# KhamLao Cooking Vocabulary (TOON format)

Thai → Lao food/cooking reference. Format below is TOON (Token-Oriented Object Notation):
- Header line declares array length and field names
- Each subsequent line is one record, comma-separated, in field order
- Quoted values use double quotes if they contain commas

"""

# Quote helper: wrap in double quotes if value contains comma
def q(v: str) -> str:
    if "," in v or '"' in v:
        return '"' + v.replace('"', '""') + '"'
    return v

toon_lines = [f"entries[{len(entries)}]{{thai,lao,note}}:"]
for e in entries:
    note = (e.get("note") or "").strip()
    toon_lines.append(f"  {q(e['thai'])},{q(e['lao'])},{q(note)}")

toon_body = frontmatter + "\n".join(toon_lines) + "\n"

SKILL_TOON.write_text(toon_body, encoding="utf-8")

# Measure
enc = tiktoken.get_encoding("cl100k_base")

orig = SKILL.read_text(encoding="utf-8")
toon = SKILL_TOON.read_text(encoding="utf-8")

orig_tokens = len(enc.encode(orig))
toon_tokens = len(enc.encode(toon))

print(f"{'Format':<10} {'Chars':>8} {'Tokens':>8} {'Chars/Tok':>10}")
print("-" * 40)
print(f"{'Markdown':<10} {len(orig):>8} {orig_tokens:>8} {len(orig)/orig_tokens:>10.2f}")
print(f"{'TOON':<10} {len(toon):>8} {toon_tokens:>8} {len(toon)/toon_tokens:>10.2f}")
print("-" * 40)
print(f"Token reduction: {(orig_tokens - toon_tokens) / orig_tokens * 100:.1f}%")
print(f"Saved {orig_tokens - toon_tokens} tokens")
