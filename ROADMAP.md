# KhamLao — Roadmap

What we want to build next, organized by impact and difficulty. Pick a task that matches your interest and skill level.

If you're new to the project, read `ARCHITECTURE.md` first.

---

## Status legend

- 🔴 **High priority** — blocks growth or affects users
- 🟡 **Medium priority** — meaningful improvement
- 🟢 **Low priority** — nice to have
- ⭐ **Difficulty 1-5** — relative implementation complexity
- 🧑‍💻 **Skill needed** — what background helps

---

## Theme 1 — Make contribution easier

KhamLao's growth depends on native Lao speakers contributing corrections. Right now the workflow requires git + Python + JSON. We need to flatten that.

### 🔴 ⭐⭐ GitHub Actions auto-build
**Goal:** When someone edits `data/*.json` via GitHub web UI, automatically run `tools/build_skills.py` and commit the regenerated `skills/*/SKILL.md`.

**Why:** A native Lao speaker can fix a single vocab entry through GitHub's web editor (no git knowledge), and the rebuild happens automatically.

**Tasks:**
- Create `.github/workflows/build.yml`
- Triggers on push/PR touching `data/**`
- Runs Python build script
- Commits regenerated skill files back to the branch
- Add validation step: check no Thai-script leaked into Lao values

**Skill needed:** 🧑‍💻 GitHub Actions, Python basics
**Effort:** 1-2 hours

### 🔴 ⭐ "Quick fix" issue template
**Goal:** Simpler issue template than current `vocab-addition.md` — just 3 fields:
- Thai word (or current wrong Lao word)
- Correct Lao word
- Why (brief reason)

Maintainer batches these into a single commit weekly.

**Tasks:**
- Add `.github/ISSUE_TEMPLATE/quick-fix.md`
- Update CONTRIBUTING.md to mention this as the easiest path

**Skill needed:** 🧑‍💻 Markdown
**Effort:** 30 min

### 🟡 ⭐⭐⭐ Web-based contribution UI
**Goal:** A simple web form (static site or lightweight backend) where contributors can submit vocab fixes without GitHub at all.

**Options:**
- GitHub Issues API + a static form (uses contributor's GitHub account)
- Google Form → spreadsheet → manual import
- Dedicated mini-app (Cloudflare Workers / Vercel)

**Skill needed:** 🧑‍💻 Frontend (HTML/JS), some backend
**Effort:** 1-3 days

---

## Theme 2 — Corpus mining

KhamLao currently has 318 vocab entries, mostly from a textbook + a Gemini bootstrap. Real Lao text (news, articles, social media) contains tens of thousands of words we don't cover.

### 🔴 ⭐⭐⭐ `tools/analyze_corpus.py`
**Goal:** Take a chunk of Lao text and identify words NOT in our current dictionary, ranked by frequency.

**Pipeline:**
1. Input: Lao text (txt file, paste, or directory)
2. Tokenize: Lao doesn't use spaces between words, so this is non-trivial. Options:
   - Whitespace-based (loses some accuracy)
   - Character n-gram based
   - Use a Lao word-segmentation library (e.g., `pylaonlp`, `lao-nlp`)
3. Frequency count
4. Diff against all `data/*.json` (flatten union of `entries[].lao` and `entries[].lao`)
5. Output top N unknown words sorted by frequency
6. Optionally: use Gemini API to auto-generate suggested Thai/English glosses

**Output formats:**
- JSON snippet ready to be added to a `data/*.json`
- Markdown report (for human review)
- Frequency CSV

**Skill needed:** 🧑‍💻 Python, basic NLP, regex
**Effort:** 1-2 days

### 🟡 ⭐⭐⭐⭐ Lao word segmenter
**Goal:** A reusable function `segment_lao(text) → list[str]` that splits Lao text into words.

**Why hard:** Lao doesn't use word boundaries. Statistical or dictionary-based methods needed.

**Options:**
- Dictionary-based (longest-match against our vocab)
- Use an existing library if any (research needed)
- Train a small model

**Skill needed:** 🧑‍💻 NLP, machine learning
**Effort:** 3-7 days

### 🟢 ⭐⭐ Corpus collection
**Goal:** A `data/corpora/` directory containing Lao text samples by category (news, social, formal).

Each file: source URL, date collected, brief description. Used to feed the analyzer.

**Skill needed:** Patience, some Lao reading
**Effort:** Ongoing

---

## Theme 3 — Expand vocabulary

The textbook bootstrap covered ป.1 fully, ป.2 partially, ป.4 partially. Many more sources exist.

### 🟡 ⭐⭐ Finish primary school textbooks
**Sources already identified (in pubhtml5.com):**
- ป.1 เล่ม 2 (LaoG1 Tb2): https://online.pubhtml5.com/maug/sjhw/
- ป.2 pages 51-150: extend via `WebFetch` on `https://pubhtml5.com/maug/usqs/basic/51-100` etc.
- ป.4 pages 51+: similar
- ป.5, ป.6: search and find

**Method:** Use `WebFetch` (or any extraction method) to pull Lao words, add to appropriate `data/*.json`.

**Skill needed:** Patience
**Effort:** 2-4 hours per textbook

### 🟡 ⭐⭐ Secondary school (ม.1-ม.7) textbooks
**Status:** Search has not found these on pubhtml5. Sources to investigate:
- Lao MOE website (moe.gov.la)
- archive.org
- UNESCO Lao education repository
- Wattay Books Laos

**Skill needed:** Research, search literacy
**Effort:** A few hours of searching + extraction

### 🟢 ⭐⭐ Domain-specific glossaries
New domains to add:
- `tech.json` — programming, internet, devices (transliterated words mainly)
- `medical.json` — body parts, illnesses, treatments
- `agriculture.json` — Lao is heavily rural; this matters
- `business.json` — formal communication, finance
- `legal.json` — government/legal terminology

For each: collect ~30-50 entries, create JSON file, add a builder in `build_skills.py`, regenerate.

**Skill needed:** Domain expertise (or willingness to research)
**Effort:** 1-3 days per domain

---

## Theme 4 — Quality and testing

### 🟡 ⭐⭐ Validation tests
**Goal:** A `tools/validate.py` script that checks all `data/*.json` for:
- No Thai-script characters in Lao values (check Unicode range)
- No duplicate Thai keys across files
- All entries have required fields
- Valid JSON

Run in CI on every PR.

**Skill needed:** 🧑‍💻 Python, regex
**Effort:** 2-3 hours

### 🟡 ⭐⭐⭐ Benchmark suite
**Goal:** A consistent way to measure KhamLao's impact.

Take a set of fixed prompts. Generate responses with skill on vs off. Compare:
- Output token count
- Thai-leak rate (count Thai-script chars in output)
- Register correctness (manual scoring)

**Skill needed:** 🧑‍💻 Python, evaluation methodology
**Effort:** 3-5 days

### 🟢 ⭐⭐⭐⭐ Native-speaker review pipeline
**Goal:** A workflow where native speakers can verify entries in batches.

Web UI shows: Thai → Lao mapping, user picks ✓/✗ or proposes correction. Submissions queue for maintainer.

**Skill needed:** 🧑‍💻 Full-stack web dev
**Effort:** 1-2 weeks

---

## Theme 5 — Distribution and discovery

### 🟡 ⭐ SEO and discoverability
- Add GitHub topics: `claude-code`, `claude-skill`, `lao-language`, `ภาษาลาว`, `lao`, `nlp`
- Submit to Anthropic skills marketplace (if there's an official one)
- Share in Lao tech communities (Facebook groups, Reddit r/laos)
- Write a launch blog post

**Skill needed:** Marketing, writing
**Effort:** 1-2 days

### 🟢 ⭐⭐ Translation of docs
README, CONTRIBUTING, ARCHITECTURE → Lao versions for native speakers who don't read English well.

**Skill needed:** Lao writing
**Effort:** 1-2 days

### 🟢 ⭐⭐⭐ Cross-LLM compatibility
KhamLao is installed for Claude Code + Gemini CLI universally. Test:
- Does it work in GitHub Copilot Chat?
- Does it work in Cursor? Aider?
- Document compatibility matrix

**Skill needed:** Multi-LLM tool familiarity
**Effort:** 2-3 days

---

## Theme 6 — Advanced features

### 🟢 ⭐⭐⭐⭐ Regional variant support
Lao has dialect variations (Vientiane, Luang Prabang, Champasak, Savannakhet). Currently we target Vientiane standard.

**Idea:** Add `region` field to entries. Optionally generate region-specific skill variants.

**Skill needed:** Linguistic knowledge, Python
**Effort:** 1 week

### 🟢 ⭐⭐⭐ Hooks + stats (like pordee)
PorDee has runtime hooks that track token savings per session. KhamLao could add:
- `~/.khamlao/state.json` for mode persistence
- `/khamlao-stats` slash command
- SessionStart hook for activation

**Skill needed:** Node.js (or any scripting), Claude Code plugin internals
**Effort:** 3-5 days

### 🟢 ⭐⭐⭐⭐⭐ Lao tokenizer optimization
Long-term: contribute to BPE tokenizer improvements upstream. Or build a custom tokenizer for Lao.

**Skill needed:** Deep NLP, ML
**Effort:** Months

---

## How to pick a task

If you're a CS student looking to contribute, here are recommended starting points based on interest:

| Interest | Try task | Time |
|---|---|---|
| Tooling/automation | GitHub Actions auto-build | weekend |
| NLP | `analyze_corpus.py` | week |
| Web dev | Web contribution UI | 1-2 weeks |
| Data wrangling | Finish primary textbooks | a few hours each |
| Testing | Validation tests | weekend |
| Linguistics | Native-speaker review (no coding needed) | ongoing |
| Distribution | SEO + outreach | weekend |

---

## How we evaluate priority

We weigh:
1. **Impact on end users** — does this help Lao speakers using Claude/Gemini?
2. **Impact on contribution velocity** — does this make adding vocab easier?
3. **Foundation work** — does this unlock future tasks?
4. **Difficulty** — can a contributor finish without burnout?

For your first contribution, prefer a small bounded task (🟢 / ⭐ / ⭐⭐) so you can ship something and learn the workflow.

---

## Open discussion topics

These are unresolved design questions worth discussing:

1. **Should we split per-grade textbook vocab vs domain vocab?** (Currently domain. Could be both.)
2. **How to handle ambiguous Lao terms** (e.g., `ຈອງ` = ladle AND "to book")? Inline notes vs separate disambiguation file?
3. **Should regional variants be in the same JSON or separate files?**
4. **Should we add a Lao→Thai mapping (reverse direction) for proofreading Lao text?**
5. **When does it make sense to publish a v2.0?** (Major restructure? Or just keep iterating on v1.x?)

Open issues/discussions for these on GitHub.
