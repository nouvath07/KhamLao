"""
One-time migration: extract vocab from existing SKILL.md into structured data/*.json
files for v1.0 modular architecture.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "khamlao" / "SKILL.md"
DATA = ROOT / "data"

skill = SKILL.read_text(encoding="utf-8")

# Parse the "General (226 entries)" table — Thai-->Lao entries
general_table = []
in_general = False
for line in skill.splitlines():
    if "### General (226 entries)" in line:
        in_general = True
        continue
    if in_general and line.startswith("### "):
        break
    # Parse table rows: | `thai` | `lao` | note |
    m = re.match(r"\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|", line)
    if m:
        general_table.append({"thai": m.group(1), "lao": m.group(2), "note": m.group(3)})

# Find natural boundary — cooking section starts at "ข้าว"
cooking_start = None
for i, e in enumerate(general_table):
    if e["thai"] == "ข้าว":
        cooking_start = i
        break
assert cooking_start is not None, "could not find 'ข้าว' boundary"
print(f"Cooking section starts at index {cooking_start}")

everyday_from_general = general_table[:cooking_start]
cooking_from_general = general_table[cooking_start:]

# Parse domain glossaries from "### 5b. Domain glossaries" section
# Format: ### Domain — | Lao | English | Note |
domain_data = {}
current_domain = None
in_5b = False
for line in skill.splitlines():
    if "### 5b. Domain glossaries" in line:
        in_5b = True
        continue
    if in_5b and line.startswith("### 6."):
        break
    # H4 = domain header
    m = re.match(r"^####\s+(\w[\w/ ]*)", line)
    if m:
        # extract domain key
        title = m.group(1).strip().lower()
        key = title.split()[0]
        current_domain = key
        domain_data[key] = []
        continue
    # Parse table row: | `lao` | english | note |
    if current_domain:
        m = re.match(r"\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|\s*(.*?)\s*\|", line)
        if m:
            lao = m.group(1)
            en = m.group(2).strip()
            note = m.group(3)
            # Skip header row "| Lao | English | Note |"
            if lao.lower() == "lao":
                continue
            domain_data[current_domain].append({"lao": lao, "en": en, "note": note})

print(f"General table: {len(general_table)} entries parsed")
print(f"  → everyday: {len(everyday_from_general)}")
print(f"  → cooking (from general): {len(cooking_from_general)}")
print(f"Domain glossaries: {sum(len(v) for v in domain_data.values())} entries")
for k, v in domain_data.items():
    print(f"  {k}: {len(v)}")

# Build the new data files

# 1. critical_fixes.json — copy from "Critical false-friends" table
critical = []
in_critical = False
for line in skill.splitlines():
    if "Critical false-friends" in line:
        in_critical = True
        continue
    if in_critical and line.startswith("###"):
        break
    m = re.match(r"\|\s*`([^`]+)`(?:\s*\([^)]*\))?\s*\|\s*`([^`]+)`(?:\s*[/]\s*`([^`]+)`)?\s*\|\s*(.*?)\s*\|", line)
    if m:
        entry = {"thai": m.group(1), "lao": m.group(2), "note": m.group(4)}
        if m.group(3):
            entry["lao_alt"] = m.group(3)
        critical.append(entry)

print(f"Critical fixes: {len(critical)}")

# Write data files
(DATA / "critical_fixes.json").write_text(
    json.dumps({"entries": critical}, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(f"Wrote data/critical_fixes.json")

# everyday: general rows 1-135 + domain glossaries verbs/objects/adjectives
everyday_full = {
    "entries": everyday_from_general,
    "extras": {
        "verbs": domain_data.get("verbs", []),
        "objects": domain_data.get("objects", []),
        "adjectives": domain_data.get("adjectives", []),
    },
}
(DATA / "everyday.json").write_text(
    json.dumps(everyday_full, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(f"Wrote data/everyday.json")

# cooking: general rows 136-226
(DATA / "cooking.json").write_text(
    json.dumps({"entries": cooking_from_general}, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(f"Wrote data/cooking.json")

# school: domain school
(DATA / "school.json").write_text(
    json.dumps({"entries": domain_data.get("school", [])}, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(f"Wrote data/school.json")

# nature: animals + body_parts + nature
nature_combined = {
    "animals": domain_data.get("animals", []),
    "body_parts": domain_data.get("body", []),  # key was "body" from "Body parts (...)"
    "nature": domain_data.get("nature", []),
}
(DATA / "nature.json").write_text(
    json.dumps(nature_combined, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(f"Wrote data/nature.json")
