# Contributing to KhamLao (ຄຳລາວ)

KhamLao is **community-driven**. Claude's Lao training data is limited, so the skill works best when native and fluent Lao speakers contribute corrections, vocabulary, and idiom guidance.

**You don't need to be a programmer to contribute.** Most contributions are language data, not code.

---

## Ways to contribute

### 1. Report Thai-influenced output (ລາຍງານ Claude ໃຊ້ຄຳໄທ)

When Claude outputs Lao that contains Thai vocabulary, Thai sentence patterns, or Thai script, open an issue using the **"Report Thai leak"** template.

You need:
- What you asked Claude
- What Claude wrote (the Thai-influenced Lao)
- What the correct Lao should be
- Why (optional but helpful)

### 2. Add vocabulary (ເພີ່ມຄຳ)

If you spot a Thai word that should map to a different Lao word, open an issue using the **"Add vocabulary"** template, or submit a PR directly editing `skills/khamlao/SKILL.md`.

### 3. Add domain glossary (ເພີ່ມຄຳສະເພາະດ້ານ)

Future versions will support domain glossaries (cooking, tech, medical, agriculture, etc.). If you have expertise in a domain, you can propose a new glossary file.

### 4. Fix register/tone errors (ແກ້ໄຂລະດັບພາສາ ຫຼື ສຽງວັນນະຍຸດ)

Lao register (formal vs casual) and tone-mark usage are subtle. Native-speaker corrections to the rules in `SKILL.md` are highly valuable.

### 5. Translate documentation

README.md and CONTRIBUTING.md are currently in English/Thai. Lao translations welcome.

---

## How to submit a PR

1. **Fork the repo** on GitHub.
2. **Clone your fork**:
   ```bash
   git clone https://github.com/<your-username>/khamlao.git
   cd khamlao
   ```
3. **Create a branch**:
   ```bash
   git checkout -b add-cooking-vocab
   ```
4. **Make your changes** — edit `skills/khamlao/SKILL.md` (or whichever file).
5. **Verify** your changes don't accidentally include Thai script where Lao is expected (visually similar characters: ก vs ກ, ข vs ຂ, etc.).
6. **Commit**:
   ```bash
   git commit -m "Add cooking vocabulary (10 entries)"
   ```
7. **Push and open a PR** on GitHub.

---

## PR checklist

Your PR will be reviewed against:

- [ ] All Lao text uses Lao Unicode block (U+0E80-U+0EFF), not Thai (U+0E00-U+0E7F)
- [ ] Tone marks are only `່` (U+0EC8) and `້` (U+0EC9) for native Lao words
- [ ] Pronoun usage follows the register rules (no `ຂ້ານ້ອຍ`)
- [ ] Future tense uses `ສິ`, not `ຈະ`
- [ ] If adding vocabulary, ideally provide a source or evidence (dictionary entry, common usage, etc.)
- [ ] If changing rules, brief explanation of why

---

## Sources/references valued in discussion

When discussing what is "correct" Lao, the following carry weight:

- Native-speaker consensus (multiple contributors agreeing)
- Lao government or academic publications
- Reputable Lao dictionaries (e.g., laoswords.com, Phouvong Phimmasone)
- Linguistic research (e.g., Somseng XAYAVONG, "Study on Word Borrowing in Lao Language" 2005)

Personal preference is welcome but acknowledged as such.

---

## Code of conduct

- Be respectful, especially when correcting others.
- Lao has regional variations (Vientiane, Luang Prabang, Champasak, etc.); when relevant, note which variant your correction applies to.
- Disagreements about "correct" Lao are normal — discuss with evidence, not assertion.
- This is a free, MIT-licensed project; contributors retain credit via git history.

---

## Maintainer notes

If you have questions before contributing, open a **discussion** (not an issue) for open-ended topics, or contact the maintainers directly.

ຂອບໃຈສຳລັບການຊ່ວຍກັນພັດທະນາພາສາລາວໃນ Claude.
