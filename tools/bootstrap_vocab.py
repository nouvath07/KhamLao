"""
Bootstrap KhamLao vocab by querying Gemini CLI for Thai → Lao mappings.

Usage:
    python tools/bootstrap_vocab.py general
    python tools/bootstrap_vocab.py cooking
    python tools/bootstrap_vocab.py all

Output: tools/vocab_raw.json (cumulative) and tools/vocab_<category>.tsv
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEEDS = ROOT / "seed_words.json"
OUT_JSON = ROOT / "vocab_raw.json"
BATCH_SIZE = 10  # words per Gemini call (avoid rate limits + timeout)

# On Windows, gemini is a .cmd shim — subprocess needs full path or shell=True
GEMINI = shutil.which("gemini") or shutil.which("gemini.cmd") or "gemini"

PROMPT_TEMPLATE = """You are a Lao language expert. For each Thai word below, provide the standard modern Lao equivalent.

Output format (strict TSV, ONE LINE PER WORD, exactly 3 fields):
THAI_WORD<TAB>LAO_WORD<TAB>NOTE

Rules:
- LAO_WORD must be in Lao script (U+0E80-U+0EFF), NEVER Thai script
- If multiple Lao equivalents exist, give the most common modern one
- NOTE is optional. Use for register hints (formal/casual), region, or false-friend warnings. Keep under 60 chars.
- Do NOT add explanations, markdown, headers, or commentary
- Do NOT skip words. If unsure, write THAI_WORD<TAB>?<TAB>uncertain

Thai words:
{words}
"""


def call_gemini(words: list[str]) -> str:
    """Call Gemini CLI with a batch of words. Returns raw stdout."""
    word_list = "\n".join(f"- {w}" for w in words)
    prompt = PROMPT_TEMPLATE.format(words=word_list)
    result = subprocess.run(
        [GEMINI, "-p", prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=300,
        shell=True,
    )
    if result.returncode != 0:
        print(f"gemini error: {result.stderr[:500]}", file=sys.stderr)
    return result.stdout


def parse_tsv(text: str) -> list[dict]:
    """Parse Gemini's TSV output into structured records."""
    records = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "-", "Warning", "Attempt", "Ripgrep")):
            continue
        # Try tab split first, then fall back to multiple spaces
        if "\t" in line:
            parts = [p.strip() for p in line.split("\t")]
        else:
            continue
        if len(parts) >= 2 and parts[0] and parts[1]:
            records.append({
                "thai": parts[0],
                "lao": parts[1],
                "note": parts[2] if len(parts) >= 3 else "",
            })
    return records


def run_category(category: str, words: list[str]) -> list[dict]:
    """Run Gemini in batches for a category, return all records."""
    all_records = []
    for i in range(0, len(words), BATCH_SIZE):
        batch = words[i:i + BATCH_SIZE]
        print(f"  batch {i//BATCH_SIZE + 1}: {len(batch)} words...", flush=True)
        raw = call_gemini(batch)
        records = parse_tsv(raw)
        print(f"    parsed {len(records)}/{len(batch)} records", flush=True)
        all_records.extend(records)
        # Save partial results between batches
        save_partial(category, all_records)
        # Small delay between batches to avoid rate limits
        if i + BATCH_SIZE < len(words):
            time.sleep(3)
    return all_records


def save_partial(category: str, records: list[dict]) -> None:
    existing = {}
    if OUT_JSON.exists():
        existing = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    existing[category] = records
    OUT_JSON.write_text(
        json.dumps(existing, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    # Also save category-specific TSV
    tsv_path = ROOT / f"vocab_{category}.tsv"
    with tsv_path.open("w", encoding="utf-8") as f:
        f.write("# Thai\tLao\tNote\n")
        for r in records:
            f.write(f"{r['thai']}\t{r['lao']}\t{r['note']}\n")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    seeds = json.loads(SEEDS.read_text(encoding="utf-8"))
    target = sys.argv[1]
    categories = list(seeds.keys()) if target == "all" else [target]
    for cat in categories:
        if cat not in seeds:
            print(f"Unknown category: {cat}", file=sys.stderr)
            continue
        print(f"=== Category: {cat} ({len(seeds[cat])} words) ===")
        records = run_category(cat, seeds[cat])
        print(f"  {cat}: {len(records)} records saved")


if __name__ == "__main__":
    main()
