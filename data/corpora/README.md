# `data/corpora/` — Lao text corpus

Raw Lao text harvested from educational sources, structured for downstream NLP work
(frequency analysis, gap-finding, evaluation sets). Not the same as `data/*.json`,
which holds curated Thai→Lao vocabulary used by the build pipeline.

## Files

| File | What's in it |
|---|---|
| `lao_textbook_corpus.jsonl` | Sentences and phrases extracted from Lao MOE textbooks. One JSON record per line. |
| `lao_mixed_script_flagged.jsonl` | Lines with >20% Thai-script characters, set aside for manual review. |
| `lao_dictionary_2022.jsonl` | *Not yet populated.* See "Dictionary" below. |

## Record schema

Textbook records:
```json
{"text": "...", "source": "textbook_p2", "grade_level": 2, "domain": "language", "script_quality": "clean", "page": 50}
```

- `script_quality`: `"clean"` (pure Lao) or `"mixed"` (Thai contamination)
- `grade_level`: 1–5 primary, 6–12 secondary (`ມ.1` = 6, `ມ.7` = 12), 0 for unknown
- `domain`: subject area — currently only `"language"` (Lao language textbooks)
- `page`: 0-based page index in the source PDF

Dictionary records (planned):
```json
{"headword": "...", "definition": "...", "source": "dictionary_2022"}
```

## Building the corpus

Use `tools/scrape_lao_corpus.py`:

```bash
# Download + render + OCR + filter, append to JSONL:
python tools/scrape_lao_corpus.py \
    --pdf-url https://lao-online.com/all_files/books/B00460.pdf \
    --source textbook_p2_old \
    --grade 2 \
    --output data/corpora/lao_textbook_corpus.jsonl
```

The pipeline:
1. Downloads the PDF (cached in temp)
2. Renders each page to PNG (PyMuPDF, default 150 DPI)
3. OCRs each PNG via Gemini CLI vision (`gemini -p ... -i page.png`)
4. Applies quality filters: drops lines with <5 Lao chars, flags >20% Thai chars as mixed
5. Appends to `lao_textbook_corpus.jsonl` (or `lao_mixed_script_flagged.jsonl`)

Requires: `pip install pymupdf` and Gemini CLI authenticated.

## Current state

The seed `lao_textbook_corpus.jsonl` contains lines extracted manually via Claude
vision from 19 sampled pages of `B00460.pdf` (ປ.2 older edition, 192 pages total)
— enough to demonstrate the schema. Running the script end-to-end on all 12
textbooks (ປ.1–5, ມ.1–7) is the actual corpus build; expect ~5–10K cleaned lines.

## Dictionary (ວັດຈະນານຸກົມ ພາສາລາວ 2022)

The 2022 Lao dictionary hosted at https://fliphtml5.com/aevfv/idgk/ is a flipbook
viewer (image tiles loaded via JavaScript). Plain `WebFetch` returns only navigation
markup, not entries. Options to extract:

1. **Find the source PDF** behind the flipbook (often available via the publisher
   or fliphtml5's download link) and run it through `scrape_lao_corpus.py` with
   a dictionary-aware prompt variant.
2. **Headless browser** (Playwright) that flips pages and downloads each tile, then
   runs vision OCR — heavier but works for any flipbook.

Either path is outside the current pipeline scope. Track progress in `ROADMAP.md`
under Theme 2 (Corpus mining).

## Quality filter rationale

- **<5 Lao chars → drop:** removes page numbers, isolated punctuation, and OCR
  artifacts. Tuned to keep short but real Lao phrases (e.g. `ດີໃຈ` = 4 chars).
- **>20% Thai chars (of Lao+Thai total) → flag mixed:** Lao textbooks should be
  pure Lao; any meaningful Thai presence is either OCR confusion (Thai/Lao look-alikes
  like `ก`/`ກ`) or a real script leak. Reviewing the flagged file catches both.
- Non-Lao non-Thai content (English, numerals, whitespace) doesn't count toward
  either bucket — those are normal in textbooks (page numbers, transliterations).
