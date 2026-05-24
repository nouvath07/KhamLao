"""
tools/scrape_lao_corpus.py - Build a Lao text corpus from scanned PDFs.

Pipeline:
    1. Download PDF (skip if --pdf-path local file is given)
    2. Render each page to PNG via PyMuPDF
    3. OCR each PNG via Gemini CLI (vision)
    4. Apply quality filters (script_quality: clean | mixed; drop if <5 Lao chars)
    5. Append records to JSONL output

Why Gemini for OCR: Tesseract has weak Lao script support; Gemini Flash handles
scanned Lao reliably and is free-tier accessible. Users without Gemini can wire
in another vision OCR by overriding `extract_text_from_image`.

Usage:
    # Full pipeline (download + render + OCR + filter):
    python tools/scrape_lao_corpus.py \\
        --pdf-url https://lao-online.com/all_files/books/B00460.pdf \\
        --source textbook_p2_old \\
        --grade 2 \\
        --output data/corpora/lao_textbook_corpus.jsonl

    # Local PDF + only first 20 pages:
    python tools/scrape_lao_corpus.py \\
        --pdf-path /tmp/p2.pdf \\
        --source textbook_p2 \\
        --grade 2 \\
        --start 0 --end 20 \\
        --output data/corpora/lao_textbook_corpus.jsonl

    # Render-only (skip OCR, useful for batch prep):
    python tools/scrape_lao_corpus.py --pdf-path /tmp/p2.pdf --render-only \\
        --pages-dir /tmp/p2_pages

Requirements:
    pip install pymupdf
    Gemini CLI installed and authenticated (https://github.com/google-gemini/gemini-cli)
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Iterator

import fitz  # PyMuPDF

LAO_RANGE = (0x0E80, 0x0EFF)
THAI_RANGE = (0x0E00, 0x0E7F)


def count_chars(text: str) -> tuple[int, int]:
    """Return (lao_char_count, thai_char_count)."""
    lao = sum(1 for c in text if LAO_RANGE[0] <= ord(c) <= LAO_RANGE[1])
    thai = sum(1 for c in text if THAI_RANGE[0] <= ord(c) <= THAI_RANGE[1])
    return lao, thai


def classify(text: str, min_lao: int = 5, thai_ratio_cutoff: float = 0.20) -> str | None:
    """
    Classify a line by script quality.

    Returns:
        "clean" — pure Lao with negligible Thai
        "mixed" — has Lao but >thai_ratio_cutoff of (Lao+Thai) chars are Thai
        None    — below min_lao threshold, drop
    """
    lao, thai = count_chars(text)
    if lao < min_lao:
        return None
    if lao + thai == 0:
        return None
    thai_ratio = thai / (lao + thai)
    return "mixed" if thai_ratio > thai_ratio_cutoff else "clean"


def download_pdf(url: str, dest: Path) -> Path:
    if dest.exists():
        print(f"[skip] PDF already exists at {dest}", file=sys.stderr)
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"[download] {url} -> {dest}", file=sys.stderr)
    urllib.request.urlretrieve(url, dest)
    return dest


def render_pages(pdf_path: Path, out_dir: Path, dpi: int = 150,
                 start: int = 0, end: int | None = None) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    end = end if end is not None else len(doc)
    paths = []
    for i in range(start, min(end, len(doc))):
        png_path = out_dir / f"page_{i:04d}.png"
        if not png_path.exists():
            pix = doc[i].get_pixmap(dpi=dpi)
            pix.save(png_path)
        paths.append(png_path)
    doc.close()
    print(f"[render] {len(paths)} pages -> {out_dir}", file=sys.stderr)
    return paths


def extract_text_from_image(png_path: Path) -> str:
    """
    OCR via Gemini CLI. Override this function to plug in a different vision model.

    The prompt asks Gemini to extract ONLY Lao text from the image, one sentence
    per line, with no Thai, English, or commentary.
    """
    gemini = shutil.which("gemini") or shutil.which("gemini.cmd")
    if gemini is None:
        raise RuntimeError(
            "Gemini CLI not found in PATH. Install from "
            "https://github.com/google-gemini/gemini-cli or override "
            "extract_text_from_image() with a different backend."
        )
    prompt = (
        "Extract ALL Lao-script text visible in this image. "
        "Output one sentence or phrase per line, in reading order. "
        "Do NOT include page numbers, English, Thai script, or commentary. "
        "If the image has no Lao text, output an empty response."
    )
    result = subprocess.run(
        [gemini, "-p", prompt, "-i", str(png_path)],
        capture_output=True, text=True, encoding="utf-8", timeout=120, shell=True,
    )
    if result.returncode != 0:
        print(f"[warn] Gemini failed on {png_path.name}: {result.stderr[:200]}", file=sys.stderr)
        return ""
    return result.stdout


def lines_from_text(text: str) -> Iterator[str]:
    for raw in text.splitlines():
        line = raw.strip()
        if line:
            yield line


def write_records(out_path: Path, records: list[dict]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def process_page(png_path: Path, source: str, grade: int,
                 domain: str = "language") -> tuple[list[dict], list[dict]]:
    """Returns (clean_records, mixed_flagged_records)."""
    text = extract_text_from_image(png_path)
    clean, mixed = [], []
    for line in lines_from_text(text):
        q = classify(line)
        if q is None:
            continue
        rec = {
            "text": line,
            "source": source,
            "grade_level": grade,
            "domain": domain,
            "script_quality": q,
        }
        (clean if q == "clean" else mixed).append(rec)
    return clean, mixed


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--pdf-url", help="URL to download the PDF from")
    src.add_argument("--pdf-path", help="Local PDF path")

    p.add_argument("--source", required=False, default="unknown",
                   help="Source tag in JSONL records (e.g. textbook_p2)")
    p.add_argument("--grade", type=int, default=0,
                   help="Grade level (1-5 primary, 6-12 secondary). Use 0 for dict/unknown.")
    p.add_argument("--domain", default="language",
                   help="Domain tag (language, math, science, etc.)")
    p.add_argument("--output", default="data/corpora/lao_textbook_corpus.jsonl",
                   help="Output JSONL for clean records")
    p.add_argument("--mixed-output", default="data/corpora/lao_mixed_script_flagged.jsonl",
                   help="Output JSONL for mixed-script records (for manual review)")
    p.add_argument("--pages-dir", default=None,
                   help="Directory to write rendered PNGs (default: system temp)")
    p.add_argument("--start", type=int, default=0, help="Start page index (0-based)")
    p.add_argument("--end", type=int, default=None, help="End page index (exclusive)")
    p.add_argument("--dpi", type=int, default=150, help="Render DPI")
    p.add_argument("--render-only", action="store_true",
                   help="Render pages then exit (skip OCR + JSONL emit)")
    args = p.parse_args()

    if args.pdf_url:
        cache = Path(tempfile.gettempdir()) / "khamlao_pdfs" / Path(args.pdf_url).name
        pdf = download_pdf(args.pdf_url, cache)
    else:
        pdf = Path(args.pdf_path)

    pages_dir = Path(args.pages_dir) if args.pages_dir else (
        Path(tempfile.gettempdir()) / "khamlao_pages" / pdf.stem
    )
    pngs = render_pages(pdf, pages_dir, dpi=args.dpi, start=args.start, end=args.end)

    if args.render_only:
        print(f"[done] rendered {len(pngs)} pages to {pages_dir}", file=sys.stderr)
        return

    out_path = Path(args.output)
    mixed_path = Path(args.mixed_output)
    total_clean = total_mixed = 0

    for png in pngs:
        clean, mixed = process_page(png, args.source, args.grade, args.domain)
        if clean:
            write_records(out_path, clean)
            total_clean += len(clean)
        if mixed:
            write_records(mixed_path, mixed)
            total_mixed += len(mixed)
        print(f"[ocr] {png.name}: +{len(clean)} clean, +{len(mixed)} mixed", file=sys.stderr)

    print(f"[done] {total_clean} clean -> {out_path}", file=sys.stderr)
    print(f"[done] {total_mixed} mixed -> {mixed_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
