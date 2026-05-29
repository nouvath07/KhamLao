---
name: khamlao
description: |
  ຄຳລາວ (KhamLao) — Lao language quality + compression skill for Claude.
  Always loaded when the user is writing or requesting Lao output.
  Covers: register (ຂ້ອຍ/ເຈົ້າ vs ຂ້າພະເຈົ້າ), tense (ສິ not ຈະ), script-only rules,
  tone marks, top false-friend Thai→Lao corrections, and a built-in vocabulary
  reference (everyday, cooking, school, nature).

  Triggers:
  - "/khamlao" / "/khamlao full" / "ຄຳລາວ" / "ໃຊ້ລາວ" / "ຕອບເປັນລາວ" → enable full
  - "/khamlao lite" → enable lite
  - "/khamlao stop" / "ຢຸດຄຳລາວ" / "ປ່ຽນເປັນປົກກະຕິ" → disable
---

# KhamLao (ຄຳລາວ)

## Persistence
ACTIVE EVERY RESPONSE that produces Lao output. ຫ້າມ drift. Off only via `/khamlao stop`.

---

## Quality Rules

### 1. Lao script only
- Never substitute Thai characters (ก ข ค) for Lao (ກ ຂ ຄ).
- If a Lao character is uncertain, say so — never fall back to Thai script.

### 2. Modern register
- **Conversation (default)**: `ຂ້ອຍ` for "I", `ເຈົ້າ` for "you". Already polite.
- **Highly formal only** (speeches, government docs): `ຂ້າພະເຈົ້າ` / `ທ່ານ` / `ພວກທ່ານ`.
- **NEVER use `ຂ້ານ້ອຍ`** — archaic, period-drama only.

### 3. Lao tense markers
- Future = **`ສິ`** (NOT `ຈະ` — that's Thai-influenced). ✅ ຂ້ອຍສິໄປ. ❌ ຂ້ອຍຈະໄປ.
- Continuous = **`ກຳລັງ`** or no marker.
- Past = **`ໄດ້`** before verb or **`ແລ້ວ`** after.

### 4. Tone marks
Only **`່`** (ໄມ້ເອກ) and **`້`** (ໄມ້ໂທ). `໊`/`໋` only for loanwords.

### 5. Critical false-friends

Most common Claude leaks:

| Thai (avoid) | Lao (use) | Note |
|---|---|---|
| `จะ` | `ສິ` | Most common Claude leak — Thai future marker leaks into Lao |
| `ใคร` | `ໃຜ` |  |
| `ที่ไหน` | `ໃສ` |  |
| `อะไร` | `ຫຍັງ` |  |
| `ขอบคุณ` | `ຂອບໃຈ` |  |
| `ไม่` | `ບໍ່` |  |
| `ทำ` | `ເຮັດ` |  |
| `เป็น` | `ແມ່ນ` |  |
| `เท่าไหร่` | `ເທົ່າໃດ` / `ທໍ່ໃດ` |  |

For broader vocabulary, see the **Vocabulary reference** section below.

### 6. Foreign words → ທັບສັບ (transliterate)
Write loanwords in Lao script by sound: file → `ໄຟລ໌`, session → `ເຊັດຊັນ`,
computer → `ຄອມພິວເຕີ້`, Claude → `ຄຣອດ`, DNA → `ດີເອັນເອ`, protein → `ໂປຣຕີນ`.

### 7. Technical identifiers stay verbatim
File paths, code, commands, URLs, function names → keep original script; describe in Lao narration.

---

## Compression Rules

### Drop these
- Polite particles when not addressing: `ເຈົ້າ`, `ນະ`, `ດ້ວຍ`
- Hedging: `ອາດຈະ`, `ໜ້າຈະ`, `ຄ່ອນຂ້າງຈະ`, `ຈິງໆ ແລ້ວ`
- Filler: `ກໍ່`, `ນັ້ນຄື`, `ນັ້ນແມ່ນ`, `ກໍ່ໝາຍຄວາມວ່າ`
- Pleasantries: `ໂດຍ` (response opener), `ໄດ້ເລີຍ`, `ແນ່ນອນ`
- English filler: just, really, basically, actually

### Verbose → terse swaps

| Verbose | Terse |
|---|---|
| ເນື່ອງຈາກ / ເພາະວ່າ | ເພາະ |
| ຫາກວ່າ / ໃນກໍລະນີທີ່ | ຖ້າ |
| ດຳເນີນການ X | X |
| ພິຈາລະນາ | ເບິ່ງ |
| ໃນການທີ່ຈະ | ເພື່ອ |
| ມີຄວາມຈຳເປັນຕ້ອງ | ຕ້ອງ |
| ດັ່ງນັ້ນ | ສະນັ້ນ / ຈິ່ງ |
| ທຳການແກ້ໄຂ | ແກ້ |
| ໂດຍທົ່ວໄປແລ້ວ | ປົກກະຕິ |

Pattern: `[ປະທານ] [ກິຣິຍາ] [ເຫດຜົນ]. [ຂັ້ນຕໍ່ໄປ].`

### Levels
| Level | Trigger | Behavior |
|---|---|---|
| **lite** | `/khamlao lite` | Drop politeness/hedging/pleasantries only. Grammar intact. |
| **full** | `/khamlao` (default) | All lite rules + drop `ການ-`/`ຄວາມ-` prefixes + fragments OK. |

---

## Auto-Clarity (drop khamlao briefly, write normal Lao, resume after)
- Security warnings (⚠️, `Warning:`)
- Irreversible commands (`DROP TABLE`, `rm -rf`, `git push --force`, `git reset --hard`)
- Multi-step sequences requiring precise order
- User asks: "ບໍ່ເຂົ້າໃຈ", "ອະທິບາຍຊັດໆ", "ບອກອີກເທື່ອ", "ງົງ"

## Boundaries (NEVER compress)
Code blocks, error messages, stack traces, file paths, URLs, technical English terms (token, function, async, render, prop) — keep exact.

---

# Vocabulary reference

Thai → Lao (and Lao → English) lookup. Apply the quality rules above to all output.


## Everyday (ປະຈຳວັນ)

Pronouns, time, family, numbers, common verbs/adjectives, emotions.

| Thai | Lao | Note |
|---|---|---|
| `ใคร` | `ໃຜ` |  |
| `ที่ไหน` | `ໃສ` |  |
| `อะไร` | `ຫຍັງ` |  |
| `ขอบคุณ` | `ຂອບໃຈ` |  |
| `ไม่` | `ບໍ່` |  |
| `ทำ` | `ເຮັດ` |  |
| `ครับ` | `ໂດຍ/ເຈົ້າ` | Politeness particle (male). Use 'ໂດຍ' for formal. |
| `ค่ะ` | `ໂດຍ/ເຈົ້າ` | Politeness particle (female). |
| `คุณ` | `ເຈົ້າ` | You (polite/general). |
| `ผม` | `ຂ້ອຍ` | I (male, polite). 'ຂ້ອຍ' is standard for both. |
| `ฉัน` | `ຂ້ອຍ` | I (female, polite). |
| `เรา` | `ເຮົາ` | We/Us. |
| `พวกเรา` | `ພວກເຮົາ` | We (group). |
| `ใช่` | `ແມ່ນ` | Yes/Correct. |
| `ไม่` | `ບໍ່` | No/Not. |
| `ไหม` | `ບໍ` | Question particle (no tone — distinct from `ບໍ່` "not"). |
| `นะ` | `ເດີ/ນາ` | Particle for emphasis/softening. |
| `ด้วย` | `ແດ່/ດ້ວຍ` | Also/With. |
| `หรือ` | `ຫຼື` | Or. |
| `และ` | `ແລະ` | And. |
| `แต่` | `ແຕ່` | But. |
| `ขอบคุณ` | `ຂອບໃຈ` | Thank you. |
| `ขอโทษ` | `ຂໍໂທດ` | Sorry/Excuse me. |
| `สวัสดี` | `ສະບາຍດີ` | Hello. |
| `ลาก่อน` | `ລາກ່ອນ` | Goodbye. |
| `ยินดีที่ได้รู้จัก` | `ຍິນດີທີ່ໄດ້ຮູ້ຈັກ` | Nice to meet you. |
| `ใคร` | `ໃຜ` | Who. |
| `อะไร` | `ຫຍັງ` | What. |
| `ที่ไหน` | `ໃສ` | Where. |
| `เมื่อไหร่` | `ຍາມໃດ` | When. |
| `ทำไม` | `ເປັນຫຍັງ` | Why. |
| `อย่างไร` | `ແນວໃດ` | How. |
| `เท่าไหร่` | `ທໍ່ໃດ` | How much. |
| `วันนี้` | `ມື້ນີ້` | Today. |
| `พรุ่งนี้` | `ມື້ອື່ນ` | Tomorrow. |
| `เมื่อวาน` | `ມື້ວານນີ້` | Yesterday. |
| `ตอนนี้` | `ຕອນນີ້` | Now. |
| `ภายหลัง` | `ພາຍຫຼັງ` | Later/Afterwards. |
| `เร็วๆ นี้` | `ໄວໆນີ້` | Soon. |
| `เช้า` | `ເຊົ້າ` | Morning. |
| `บ่าย` | `ສວາຍ` | Afternoon. ❌ Avoid `ບ່າຍ` (Thai loanword). |
| `เย็น` | `ແລງ` | Evening. |
| `กลางคืน` | `ກາງຄືນ` | Night. |
| `เที่ยง` | `ທ່ຽງ` | Noon. |
| `หนึ่ง` | `ໜຶ່ງ` | One. |
| `สอง` | `ສອງ` | Two. |
| `สาม` | `ສາມ` | Three. |
| `สี่` | `ສີ່` | Four. |
| `ห้า` | `ຫ້າ` | Five. |
| `หก` | `ຫົກ` | Six. |
| `เจ็ด` | `ເຈັດ` | Seven. |
| `แปด` | `ແປດ` | Eight. |
| `เก้า` | `ເກົ້າ` | Nine. |
| `สิบ` | `ສິບ` | Ten. |
| `ร้อย` | `ຮ້ອຍ` | Hundred. |
| `พัน` | `ພັນ` | Thousand. |
| `หมื่น` | `ໝື່ນ` | Ten thousand. |
| `แสน` | `ແສນ` | Hundred thousand. |
| `ล้าน` | `ລ້ານ` | Million. |
| `พ่อ` | `ພໍ່` | Father. |
| `แม่` | `ແມ່` | Mother. |
| `ลูก` | `ລູກ` | Child. |
| `พี่` | `ອ້າຍ/ເອື້ອຍ` | Older brother/sister. |
| `น้อง` | `ນ້ອງ` | Younger sibling. |
| `ปู่` | `ປູ່` | Paternal grandfather. |
| `ย่า` | `ຍ່າ` | Paternal grandmother. |
| `ตา` | `ພໍ່ຕູ້` | Maternal grandfather. Vientiane standard. Variants: `ພໍ່ເຖົ້າ`. ❌ Avoid `ຕາ` (Thai loanword). |
| `ยาย` | `ແມ່ຕູ້` | Maternal grandmother. Vientiane standard. Variants: `ແມ່ເຖົ້າ`. ❌ Avoid `ຍາຍ` (Thai loanword). |
| `ลุง` | `ລຸງ` | Uncle (older). |
| `ป้า` | `ປ້າ` | Aunt (older). |
| `น้า` | `ນ້າ` | Maternal aunt/uncle (younger). |
| `อา` | `ອາ` | Paternal aunt/uncle (younger). |
| `หลาน` | `ຫຼານ` | Grandchild/Niece/Nephew. |
| `ผู้ชาย` | `ຜູ້ຊາຍ` | Man. |
| `ผู้หญิง` | `ຜູ້ຍິງ` | Woman. |
| `เด็ก` | `ເດັກນ້ອຍ` | Child/Kid. |
| `ผู้ใหญ่` | `ຜູ້ໃຫຍ່` | Adult. |
| `คน` | `ຄົນ` | Person. |
| `เพื่อน` | `ໝູ່` | Friend. |
| `บ้าน` | `ເຮືອນ` | House/Home. |
| `ห้อง` | `ຫ້ອງ` | Room. |
| `ห้องน้ำ` | `ຫ້ອງນ້ຳ` | Bathroom. |
| `ครัว` | `ເຮືອນຄົວ` | Kitchen. |
| `โต๊ะ` | `ໂຕະ` | Table. |
| `เก้าอี้` | `ຕັ່ງ` | Chair. |
| `เตียง` | `ຕຽງ` | Bed. |
| `ประตู` | `ປະຕູ` | Door. |
| `หน้าต่าง` | `ປ່ອງຢ້ຽມ` | Window. |
| `ไป` | `ໄປ` | Go. |
| `มา` | `ມາ` | Come. |
| `อยู่` | `ຢູ່` | Stay/Be. |
| `ทำ` | `ເຮັດ` | Do/Make. |
| `กิน` | `ກິນ` | Eat. |
| `ดื่ม` | `ດື່ມ` | Drink. |
| `นอน` | `ນອນ` | Sleep. |
| `พูด` | `ເວົ້າ` | Speak/Talk. |
| `ฟัง` | `ຟັງ` | Listen. |
| `เห็น` | `ເຫັນ` | See. |
| `ดู` | `ເບິ່ງ` | Watch/Look. |
| `อ่าน` | `ອ່ານ` | Read. |
| `เขียน` | `ຂຽນ` | Write. |
| `ซื้อ` | `ຊື້` | Buy. |
| `ขาย` | `ຂາຍ` | Sell. |
| `ใหญ่` | `ໃຫຍ່` | Big. |
| `เล็ก` | `ນ້ອຍ` | Small. |
| `ดี` | `ດີ` | Good. |
| `ไม่ดี` | `ບໍ່ດີ` | Bad. |
| `สวย` | `ງາມ` | Beautiful. |
| `น่าเกลียด` | `ຂີ້ຮ້າຍ` | Ugly. |
| `ใหม่` | `ໃໝ່` | New. |
| `เก่า` | `ເກົ່າ` | Old. |
| `ร้อน` | `ຮ້ອນ` | Hot. |
| `เย็น` | `ເຢັນ` | Cold. |
| `หวาน` | `ຫວານ` | Sweet. |
| `เปรี้ยว` | `ສົ້ມ` | Sour. |
| `เค็ม` | `ເຄັມ` | Salty. |
| `เผ็ด` | `ເຜັດ` | Spicy. |
| `เร็ว` | `ໄວ` | Fast. |
| `ช้า` | `ຊ້າ` | Slow. |
| `ใกล้` | `ໃກ້` | Near. |
| `ไกล` | `ໄກ` | Far. |
| `มาก` | `ຫຼາຍ` | Very/Many. |
| `น้อย` | `ໜ້ອຍ` | Little/Few. |
| `หลาย` | `ຫຼາຍ` | Many. |
| `บาง` | `ບາງ` | Some. |
| `เงิน` | `ເງິນ` | Money. |
| `ราคา` | `ລາຄາ` | Price. |
| `แพง` | `ແພງ` | Expensive. |
| `ถูก` | `ຖືກ` | Cheap. |
| `รัก` | `ຮັກ` | Love. |
| `ชอบ` | `ມັກ` | Like. |
| `เกลียด` | `ຊັງ` | Hate. |
| `ดีใจ` | `ດີໃຈ` | Happy/Glad. |
| `เศร้า` | `ເສຍໃຈ` | Sad. |
| `โกรธ` | `ສູນ/ຄຽດ` | Angry. |
| `กลัว` | `ຢ້ານ` | Afraid. |
| `เหนื่อย` | `ເມື່ອຍ` | Tired. |
| `หิว` | `ຫິວ` | Hungry. |
| `อิ่ม` | `ອີ່ມ` | Full (stomach). |
| `เจ็บ` | `ເຈັບ` | Hurt/Pain. |
| `ป่วย` | `ບໍ່ສະບາຍ` | Sick / unwell (general). ⚠️ `ໄຂ້` means "fever" specifically, not generic sickness. |

### Verbs (from MOE textbooks)

| Lao | English | Note |
|---|---|---|
| `ຮຽນ` | to study/learn |  |
| `ຮູ້` | to know |  |
| `ຂັບ` | to drive |  |
| `ຢືນ` | to stand |  |
| `ຍ່າງ` | to walk |  |
| `ບິນ` | to fly |  |
| `ຍິ້ມ` | to smile |  |
| `ຫຼັບ` | to sleep (close eyes) |  |
| `ອາບນ້ຳ` | to bathe |  |
| `ຮັບ` | to receive |  |
| `ປູກ` | to plant/grow |  |
| `ຂຸດ` | to dig |  |
| `ຈູບ` | to kiss |  |
| `ຢຸດ` | to stop |  |
| `ຫຍິບ` | to sew |  |

### Common objects

| Lao | English | Note |
|---|---|---|
| `ລົດ` | car/vehicle |  |
| `ລົດຖີບ` | bicycle |  |
| `ສະບູ` | soap |  |
| `ເສື້ອຜ້າ` | clothes |  |
| `ສຽງ` | sound/voice |  |
| `ຕຶກ` | building |  |
| `ທຸງ` | flag |  |
| `ມຸ້ງ` | mosquito net |  |
| `ຫິ້ງ` | shelf |  |
| `ໂມງ` | clock/hour |  |

### Adjectives

| Lao | English | Note |
|---|---|---|
| `ສີ` | color |  |
| `ຍາວ` | long |  |
| `ສູງ` | tall/high |  |
| `ມືດ` | dark |  |
| `ຕື້ນ` | shallow |  |
| `ປອດໄພ` | safe |  |

## Cooking (ການເຮັດອາຫານ)

Ingredients, methods, utensils, tastes, dishes.

| Thai | Lao | Note |
|---|---|---|
| `ข้าว` | `ເຂົ້າ` | Rice. |
| `ข้าวสาร` | `ເຂົ້າສານ` | Raw rice. |
| `ข้าวสวย` | `ເຂົ້າຈ້າວ` | Cooked jasmine rice. |
| `ข้าวเหนียว` | `ເຂົ້າໜຽວ` | Sticky rice. |
| `เส้นก๋วยเตี๋ยว` | `ເສັ້ນເຝີ` | Noodle (flat rice noodle). |
| `เส้นหมี่` | `ເສັ້ນໝີ່` | Rice vermicelli. |
| `บะหมี่` | `ໝີ່` | Egg noodles. |
| `น้ำ` | `ນ້ຳ` | Water. |
| `น้ำตาล` | `ນ້ຳຕານ` | Sugar. |
| `เกลือ` | `ເກືອ` | Salt. |
| `น้ำปลา` | `ນ້ຳປາ` | Fish sauce. |
| `น้ำมัน` | `ນ້ຳມັນ` | Oil. |
| `ซีอิ๊ว` | `ຊີອິ້ວ` | Soy sauce. |
| `ซอส` | `ຊອດ` | Sauce. |
| `พริก` | `ໝາກເຜັດ` | Chili. (per Lao MOE ป.1 textbook; `ໝາກພິກ` is less common.) |
| `พริกไทย` | `ພິກໄທ` | Pepper. |
| `กระเทียม` | `ກະທຽມ` | Garlic. |
| `หอม` | `ຫອມ` | Onion/Shallot/Fragrant. |
| `หอมแดง` | `ຫອມບົ່ວ` | Shallot. |
| `ขิง` | `ຂີງ` | Ginger. |
| `ข่า` | `ຂ່າ` | Galangal. |
| `ตะไคร้` | `ຫົວສິງໄຄ` | Lemongrass. |
| `ใบมะกรูด` | `ໃບບັກຂີ້ຫູດ` | Kaffir lime leaf. |
| `ผักชี` | `ຜັກຫອມປ້ອມ` | Coriander/Cilantro. |
| `ใบโหระพา` | `ໃບລະພາ` | Sweet basil. |
| `ใบกระเพรา` | `ໃບກະເພົາ` | Holy basil. |
| `ไก่` | `ໄກ່` | Chicken. |
| `หมู` | `ໝູ` | Pork. |
| `เนื้อ` | `ຊີ້ນ` | Meat (usually beef in Lao). |
| `ปลา` | `ປາ` | Fish. |
| `กุ้ง` | `ກຸ້ງ` | Shrimp/Prawn. |
| `ปู` | `ປູ` | Crab. (`ກະປູ` also acceptable.) |
| `ไข่` | `ໄຂ່` | Egg. |
| `ไส้กรอก` | `ໄສ້ອົ້ວ` | Sausage. |
| `ผัก` | `ຜັກ` | Vegetable. |
| `ผักกาด` | `ຜັກກາດ` | Chinese cabbage/Mustard green. |
| `ผักบุ้ง` | `ຜັກບົ້ງ` | Morning glory. |
| `มะเขือ` | `ໝາກເຂືອ` | Eggplant. |
| `มะเขือเทศ` | `ໝາກເລັ່ນ` | Tomato. |
| `ฟัก` | `ໝາກຟັກ` | Winter melon. |
| `ฟักทอง` | `ໝາກອຶ` | Pumpkin. |
| `แตงกวา` | `ໝາກແຕງ` | Cucumber. |
| `ถั่ว` | `ໝາກຖົ່ວ` | Bean/Peanut. |
| `ผลไม้` | `ໝາກໄມ້` | Fruit. |
| `กล้วย` | `ໝາກກ້ວຍ` | Banana. |
| `มะม่วง` | `ໝາກມ່ວງ` | Mango. |
| `ส้ม` | `ໝາກກ້ຽງ` | Orange. |
| `แตงโม` | `ໝາກໂມ` | Watermelon. |
| `มะละกอ` | `ໝາກຫຸ່ງ` | Papaya. |
| `ทุเรียน` | `ໝາກຖຸລຽນ` | Durian. |
| `เงาะ` | `ໝາກເງາະ` | Rambutan. |
| `ลำไย` | `ໝາກລຳໄຍ` | Longan. |
| `ลิ้นจี่` | `ໝາກລິ້ນຈີ່` | Lychee. |
| `ต้ม` | `ຕົ້ມ` | Boil. |
| `ผัด` | `ຂົ້ວ` | Stir-fry. 'ຜັດ' is also used but 'ຂົ້ວ' is more Lao. |
| `ทอด` | `ຈືນ` | Deep-fry. 'ທອດ' is also used. |
| `ย่าง` | `ປີ້ງ` | Grill (Lao uses 'ປີ້ງ' more than 'ຍ່າງ'). |
| `ปิ้ง` | `ປີ້ງ` | Grill/Toast. |
| `นึ่ง` | `ໜຶ້ງ` | Steam. |
| `แกง` | `ແກງ` | Soup/Curry. |
| `หุง` | `ຫຸງ` | Cook (rice). |
| `ตำ` | `ຕຳ` | Pound (in mortar). |
| `หั่น` | `ຊອຍ` | Slice/Cut. |
| `สับ` | `ຟັກ` | Chop/Mince. |
| `บด` | `ບົດ` | Grind. |
| `หม้อ` | `ໝໍ້` | Pot. |
| `กระทะ` | `ໝໍ້ຂົ້ວ` | Pan/Skillet. |
| `ทัพพี` | `ຈອງ` | Ladle. ⚠️ Homonym with `ຈອງ` "to book/reserve". |
| `ช้อน` | `ບ່ວງ` | Spoon. |
| `ส้อม` | `ສ້ອມ` | Fork. |
| `มีด` | `ພ້າ/ມີດ` | Knife. |
| `เขียง` | `ຂຽງ` | Cutting board. |
| `ตะหลิว` | `ຈອງ` | Spatula. Same word as ladle in Lao (one term covers both). ⚠️ Homonym with `ຈອງ` "to book/reserve". |
| `ครก` | `ຄົກ` | Mortar. |
| `สาก` | `ສາກ` | Pestle. |
| `ร้อน` | `ຮ້ອນ` | Hot. |
| `เย็น` | `ເຢັນ` | Cold. |
| `อุ่น` | `ອຸ່ນ` | Warm. |
| `ดิบ` | `ດິບ` | Raw. |
| `สุก` | `ສຸກ` | Cooked/Ripe. |
| `อร่อย` | `ແຊບ` | Delicious. |
| `ไม่อร่อย` | `ບໍ່ແຊບ` | Not delicious. |
| `ขม` | `ຂົມ` | Bitter. |
| `จืด` | `ຈືດ` | Bland. |
| `ส้มตำ` | `ຕຳໝາກຫຸ່ງ` | Papaya salad. |
| `ลาบ` | `ລາບ` | Larb (minced meat salad). |
| `ต้มยำ` | `ຕົ້ມຍຳ` | Tom Yum soup. |
| `แกงเขียวหวาน` | `ແກງຂຽວຫວານ` | Green curry. |
| `ผัดไทย` | `ຜັດໄທ` | Pad Thai. |
| `ข้าวเหนียวมะม่วง` | `ເຂົ້າໜຽວໝາກມ່ວງ` | Mango sticky rice. |

## School (ໂຮງຮຽນ)

From Lao MOE ປ.1-ປ.4 textbooks.

| Lao | English | Note |
|---|---|---|
| `ໂຮງຮຽນ` | school |  |
| `ຫ້ອງຮຽນ` | classroom |  |
| `ນັກຮຽນ` | student |  |
| `ຄູ` | teacher |  |
| `ນາຍຄູ` | teacher (male, respectful) |  |
| `ບົດຮຽນ` | lesson |  |
| `ສົກຮຽນ` | school year |  |
| `ປຶ້ມ` | book |  |
| `ຄໍາສັບ` | vocabulary |  |
| `ໄວຍາກອນ` | grammar |  |
| `ຫົວບົດ` | topic/heading |  |
| `ປະໂຫຍກ` | sentence |  |
| `ວັກ` | paragraph |  |
| `ຕົວເລກ` | number/numeral |  |
| `ຫັດຂຽນ` | writing practice |  |

## Nature (ທໍາມະຊາດ)

From Lao MOE ປ.1-ປ.4 textbooks.


### Animals (ສັດ)

| Lao | English | Note |
|---|---|---|
| `ເສືອ` | tiger |  |
| `ໝາ` | dog |  |
| `ງູ` | snake |  |
| `ເຕົ່າ` | turtle |  |
| `ລີງ` | monkey |  |
| `ແຮດ` | rhinoceros |  |
| `ນົກ` | bird |  |
| `ມ້າ` | horse |  |
| `ກາ` | crow |  |
| `ຊ້າງ` | elephant |  |
| `ຄວາຍ` | buffalo |  |
| `ງົວ` | cow |  |
| `ຍຸງ` | mosquito |  |

### Body parts (ສ່ວນຮ່າງກາຍ)

| Lao | English | Note |
|---|---|---|
| `ຫາງ` | tail |  |
| `ຂາ` | leg |  |
| `ຕາ` | eye | homonym: ຕາ also = Thai-loaned 'maternal grandfather' (avoid that use; see ພໍ່ຕູ້) |
| `ຫູ` | ear |  |
| `ຜິວ` | skin |  |
| `ປາກ` | mouth |  |
| `ຕີນ` | foot |  |
| `ກະດູກ` | bone |  |

### Nature (ທໍາມະຊາດ)

| Lao | English | Note |
|---|---|---|
| `ປ່າ` | forest |  |
| `ຕົ້ນໄມ້` | tree |  |
| `ຟ້າ` | sky |  |
| `ໄຮ່` | field/farm |  |
| `ຕາຝັ່ງ` | riverbank |  |
| `ດາວ` | star |  |
| `ສາຍນ້ຳ` | stream/water flow |  |
| `ຫຍ້າ` | grass |  |
| `ໄມ້` | wood |  |
| `ທໍາມະຊາດ` | nature |  |
| `ຕາເວັນ` | sun |  |
