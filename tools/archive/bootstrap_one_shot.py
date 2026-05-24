"""One-shot vocab generation: send whole category in single Gemini call."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
SEEDS = ROOT / "seed_words.json"
GEMINI = shutil.which("gemini") or shutil.which("gemini.cmd") or "gemini"

PROMPT_TEMPLATE = """You are a Lao language expert. For each Thai word below, provide the standard modern Lao equivalent.

Output format (strict TSV, ONE LINE PER WORD, exactly 3 fields):
THAI_WORD<TAB>LAO_WORD<TAB>NOTE

Rules:
- LAO_WORD must be in Lao script (U+0E80-U+0EFF), NEVER Thai script
- If multiple Lao equivalents exist, give the most common modern one
- NOTE is a short English meaning gloss (under 60 chars)
- Do NOT add explanations, markdown, headers, or commentary
- Do NOT skip words

Thai words ({category} domain):
{words}
"""


def run(category: str) -> None:
    seeds = json.loads(SEEDS.read_text(encoding="utf-8"))
    if category not in seeds:
        print(f"unknown: {category}", file=sys.stderr)
        sys.exit(1)
    words = seeds[category]
    prompt = PROMPT_TEMPLATE.format(
        category=category,
        words="\n".join(f"- {w}" for w in words),
    )
    print(f"Sending {len(words)} {category} words to Gemini...", file=sys.stderr)
    result = subprocess.run(
        [GEMINI, "-p", prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=600,
        shell=True,
    )
    out_tsv = ROOT / f"vocab_{category}.tsv"
    out_tsv.write_text("# Thai\tLao\tNote\n" + result.stdout, encoding="utf-8")
    print(f"Wrote {out_tsv}", file=sys.stderr)
    print(result.stdout)
    if result.stderr:
        print("---STDERR---", file=sys.stderr)
        print(result.stderr[:500], file=sys.stderr)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "cooking")
