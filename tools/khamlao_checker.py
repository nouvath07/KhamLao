"""
khamlao_checker — quality / correctness checks for Lao text.

A standalone detector for the most common defects in machine-generated Lao
(LLM output, OCR, TTS transcripts):

    1. Thai-script leaks      — Thai Unicode chars in supposedly-Lao text
    2. Thai-word leaks        — Thai-script words with known Lao corrections
    3. Lao-script Thai-isms   — Lao-script words that are Thai-influenced
                                (e.g. ຈະ instead of ສິ for the future marker)
    4. Archaic pronouns       — e.g. ຂ້ານ້ອຍ (period-drama register)
    5. Invalid tone marks     — ໊ ໋ on native words (valid only in loanwords)

This is "Layer 2" of the KhamLao quality stack: the rules in data/*.json
(Layer 1) made callable from any Lao NLP pipeline, not just an LLM prompt.

Usage (library):
    from khamlao_checker import check
    report = check("ຂ້ອຍຈະໄປເຮັດວຽກ")
    print(report["score"], report["lao_script_thaiisms"])

Usage (CLI):
    echo "ຂ້ອຍຈະໄປ" | python tools/khamlao_checker.py
    python tools/khamlao_checker.py "ຂ້ານ້ອຍຈະໄປ"

    # Lint files for Thai-script leaks (exits non-zero if any found — CI/hook):
    python tools/khamlao_checker.py --file examples/coffee-shop.html
    python tools/khamlao_checker.py --file skills/khamlao/SKILL.md data/web.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

LAO_RANGE = (0x0E80, 0x0EFF)
THAI_RANGE = (0x0E00, 0x0E7F)

# Lao tone marks valid in native words: MAI EK (U+0EC8), MAI THO (U+0EC9).
# MAI TI (U+0ECA) and MAI CATAWA (U+0ECB) appear only in loanwords/foreign names.
NONSTANDARD_TONE_MARKS = {"໊", "໋"}

# Lao-script words that are Thai-influenced — written in correct Lao script but
# the wrong word choice. Curated, high-confidence only. {leak: (correct, why)}.
LAO_SCRIPT_THAIISMS: dict[str, tuple[str, str]] = {
    "ຈະ": ("ສິ", "Thai-influenced future marker; Lao uses ສິ"),
    "ໄຫມ": ("ບໍ", "Thai ไหม question particle; Lao puts ບໍ at clause end"),
    "ໄໝ": ("ບໍ", "Thai ไหม question particle; Lao puts ບໍ at clause end"),
    "ໃຊ່": ("ແມ່ນ", "Thai ใช่; Lao affirmative is ແມ່ນ"),
    "ຄ່ະ": ("ເຈົ້າ", "Thai ค่ะ politeness particle; not standard Lao"),
    "ດ້ວຍ": ("ນຳ", "Thai-leaning ด้วย; Lao often prefers ນຳ for 'with/too'"),
}

# Archaic / wrong-register pronouns. {found: (suggest, why)}.
ARCHAIC_PRONOUNS: dict[str, tuple[str, str]] = {
    "ຂ້ານ້ອຍ": ("ຂ້ອຍ", "archaic first-person; period-drama register only"),
}

# Pronoun sets for register classification.
FORMAL_PRONOUNS = {"ຂ້າພະເຈົ້າ", "ທ່ານ", "ພວກທ່ານ"}
MODERN_PRONOUNS = {"ຂ້ອຍ", "ເຈົ້າ", "ພວກເຮົາ", "ເຮົາ"}


def _data_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "data"


def _load_thai_word_map() -> dict[str, tuple[str, str]]:
    """
    Build {thai_script_word: (correct_lao, source)} from data/*.json.

    Any entry with a `thai` field becomes a leak signature: if that Thai-script
    word shows up in supposedly-Lao text, it's a leak and we can suggest the Lao.
    """
    mapping: dict[str, tuple[str, str]] = {}
    data_dir = _data_dir()
    if not data_dir.exists():
        return mapping
    for jf in sorted(data_dir.glob("*.json")):
        try:
            obj = json.loads(jf.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        entries = obj.get("entries", []) if isinstance(obj, dict) else []
        for e in entries:
            thai = (e.get("thai") or "").strip()
            lao = (e.get("lao") or "").strip()
            if thai and lao:
                mapping.setdefault(thai, (lao, jf.stem))
    return mapping


_THAI_WORD_MAP = _load_thai_word_map()


def count_chars(text: str) -> tuple[int, int]:
    """Return (lao_char_count, thai_char_count)."""
    lao = sum(1 for c in text if LAO_RANGE[0] <= ord(c) <= LAO_RANGE[1])
    thai = sum(1 for c in text if THAI_RANGE[0] <= ord(c) <= THAI_RANGE[1])
    return lao, thai


def detect_thai_script(text: str) -> dict:
    lao, thai = count_chars(text)
    total = lao + thai
    chars = [(i, c) for i, c in enumerate(text)
             if THAI_RANGE[0] <= ord(c) <= THAI_RANGE[1]]
    return {
        "count": thai,
        "ratio": (thai / total) if total else 0.0,
        "chars": chars,
    }


def detect_thai_words(text: str) -> list[dict]:
    """Thai-script words (from data/*.json) appearing in the text."""
    found = []
    for thai, (lao, source) in _THAI_WORD_MAP.items():
        if thai in text:
            found.append({"found": thai, "suggest": lao, "source": source})
    return found


def detect_lao_script_thaiisms(text: str) -> list[dict]:
    found = []
    for leak, (correct, why) in LAO_SCRIPT_THAIISMS.items():
        if leak in text:
            found.append({"found": leak, "suggest": correct, "note": why})
    return found


def detect_archaic_pronouns(text: str) -> list[dict]:
    found = []
    for arch, (suggest, why) in ARCHAIC_PRONOUNS.items():
        if arch in text:
            found.append({"found": arch, "suggest": suggest, "note": why})
    return found


def detect_invalid_tone_marks(text: str) -> list[tuple[int, str]]:
    return [(i, c) for i, c in enumerate(text) if c in NONSTANDARD_TONE_MARKS]


def classify_register(text: str) -> str:
    has_archaic = any(a in text for a in ARCHAIC_PRONOUNS)
    has_formal = any(p in text for p in FORMAL_PRONOUNS)
    # Strip formal/archaic matches before checking modern: ເຈົ້າ is a substring
    # of ຂ້າພະເຈົ້າ, so naive matching would mis-tag formal text as "mixed".
    residual = text
    for p in (*FORMAL_PRONOUNS, *ARCHAIC_PRONOUNS):
        residual = residual.replace(p, "")
    has_modern = any(p in residual for p in MODERN_PRONOUNS)
    if has_archaic:
        return "archaic"
    if has_formal and has_modern:
        return "mixed"
    if has_formal:
        return "formal"
    if has_modern:
        return "modern"
    return "unknown"


def check(text: str) -> dict:
    """
    Run all checks and return a report. `score` is 1.0 for clean text,
    reduced by each defect class found.
    """
    thai_script = detect_thai_script(text)
    thai_words = detect_thai_words(text)
    lao_thaiisms = detect_lao_script_thaiisms(text)
    archaic = detect_archaic_pronouns(text)
    bad_tones = detect_invalid_tone_marks(text)

    # Score: start at 1.0, subtract weighted penalties (floor 0.0).
    score = 1.0
    score -= min(thai_script["ratio"], 0.5)          # up to -0.5 for Thai script
    score -= 0.15 * len(lao_thaiisms)                # each Lao-script Thai-ism
    score -= 0.20 * len(archaic)                     # archaic pronoun
    score -= 0.05 * len(bad_tones)                   # each bad tone mark
    score = max(0.0, round(score, 3))

    issues = (
        (1 if thai_script["count"] else 0)
        + len(lao_thaiisms) + len(archaic) + len(bad_tones)
    )

    return {
        "text": text,
        "thai_script": thai_script,
        "thai_word_leaks": thai_words,
        "lao_script_thaiisms": lao_thaiisms,
        "archaic_pronouns": archaic,
        "invalid_tone_marks": bad_tones,
        "register": classify_register(text),
        "issues": issues,
        "score": score,
    }


def _format_report(r: dict) -> str:
    lines = [f"score: {r['score']}  register: {r['register']}  issues: {r['issues']}"]
    ts = r["thai_script"]
    if ts["count"]:
        sample = "".join(c for _, c in ts["chars"][:10])
        lines.append(f"  thai-script: {ts['count']} chars (ratio {ts['ratio']:.2f}) e.g. {sample!r}")
    for w in r["thai_word_leaks"]:
        lines.append(f"  thai-word leak: {w['found']} → {w['suggest']}  [{w['source']}]")
    for t in r["lao_script_thaiisms"]:
        lines.append(f"  Lao-script Thai-ism: {t['found']} → {t['suggest']}  ({t['note']})")
    for a in r["archaic_pronouns"]:
        lines.append(f"  archaic: {a['found']} → {a['suggest']}  ({a['note']})")
    if r["invalid_tone_marks"]:
        positions = [i for i, _ in r["invalid_tone_marks"]]
        lines.append(f"  invalid tone marks at positions {positions}")
    return "\n".join(lines)


def check_file(path: str) -> tuple[list[tuple[int, int, str]], int]:
    """
    Scan a file for Thai-script leaks, line by line.

    Returns (leaks, total) where leaks is [(line_no, thai_char_count, fragment)]
    and total is the sum of Thai-script chars across the file. Works on any text
    file (HTML, JSON, md) — Thai-script detection ignores English/code/markup.
    """
    text = Path(path).read_text(encoding="utf-8")
    leaks = []
    for i, line in enumerate(text.splitlines(), 1):
        ts = detect_thai_script(line)
        if ts["count"]:
            frag = "".join(c for _, c in ts["chars"])
            leaks.append((i, ts["count"], frag))
    total = sum(n for _, n, _ in leaks)
    return leaks, total


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows cp1252 guard
    except AttributeError:
        pass

    args = sys.argv[1:]

    # --file mode: lint one or more files for Thai-script leaks (CI-friendly,
    # exits non-zero if any leak is found). The point KhamLao learned the hard
    # way: a detector only helps if it's actually run over generated output.
    if args and args[0] == "--file":
        paths = args[1:]
        if not paths:
            print("usage: khamlao_checker.py --file <path> [<path> ...]")
            sys.exit(2)
        any_leak = False
        for p in paths:
            leaks, total = check_file(p)
            if total:
                any_leak = True
                print(f"✗ {p}: {total} Thai-script chars on {len(leaks)} line(s)")
                for ln, _, frag in leaks[:40]:
                    print(f"    L{ln}: {frag!r}")
                if len(leaks) > 40:
                    print(f"    ... and {len(leaks) - 40} more line(s)")
            else:
                print(f"✓ {p}: clean (no Thai-script leak)")
        sys.exit(1 if any_leak else 0)

    # text mode: check a string from argv or stdin
    text = " ".join(args) if args else sys.stdin.read()
    print(_format_report(check(text)))


if __name__ == "__main__":
    main()
