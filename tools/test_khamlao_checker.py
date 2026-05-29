"""
Tests for khamlao_checker. Run: python tools/test_khamlao_checker.py
Pure stdlib (no pytest dependency) so contributors can run it with zero setup.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from khamlao_checker import (  # noqa: E402
    check,
    check_file,
    classify_register,
    detect_invalid_tone_marks,
    detect_lao_script_thaiisms,
    detect_thai_script,
)

_passed = 0
_failed = 0


def expect(name: str, cond: bool) -> None:
    global _passed, _failed
    if cond:
        _passed += 1
    else:
        _failed += 1
        print(f"  FAIL: {name}")


# --- clean Lao: should score 1.0, no issues ---
clean = check("ຂ້ອຍສິໄປເຮັດວຽກຢູ່ໂຮງຮຽນ")
expect("clean score == 1.0", clean["score"] == 1.0)
expect("clean has no issues", clean["issues"] == 0)
expect("clean register modern", clean["register"] == "modern")

# --- Lao-script Thai-ism: ຈະ should be flagged, suggest ສິ ---
leaky = check("ຂ້ອຍຈະໄປເຮັດວຽກ")
expect("ຈະ detected", any(t["found"] == "ຈະ" for t in leaky["lao_script_thaiisms"]))
expect("ຈະ suggests ສິ", leaky["lao_script_thaiisms"][0]["suggest"] == "ສິ")
expect("leaky score < 1.0", leaky["score"] < 1.0)

# --- Thai script leak: real Thai characters in text ---
thai_mix = check("ຂ້ອຍไปไหน")
expect("thai script counted", thai_mix["thai_script"]["count"] > 0)
expect("thai script ratio > 0", thai_mix["thai_script"]["ratio"] > 0)

# --- archaic pronoun: ຂ້ານ້ອຍ ---
arch = check("ຂ້ານ້ອຍຈະໄປ")
expect("archaic detected", len(arch["archaic_pronouns"]) == 1)
expect("archaic suggests ຂ້ອຍ", arch["archaic_pronouns"][0]["suggest"] == "ຂ້ອຍ")
expect("archaic register", arch["register"] == "archaic")

# --- invalid tone marks: ໊ ໋ ---
bad_tone = detect_invalid_tone_marks("ນ໊ໍ")
expect("invalid tone mark detected", len(bad_tone) >= 1)
expect("clean has no bad tone marks", len(detect_invalid_tone_marks("ຂ້ອຍ")) == 0)

# --- register classification ---
expect("formal register", classify_register("ຂ້າພະເຈົ້າຂໍຂອບໃຈທ່ານ") == "formal")
expect("mixed register", classify_register("ຂ້າພະເຈົ້າ ແລະ ຂ້ອຍ") == "mixed")
expect("unknown register", classify_register("ໄປໂຮງຮຽນ") == "unknown")

# --- detect_thai_script on pure Lao returns zero ---
expect("pure Lao no thai script", detect_thai_script("ສະບາຍດີ")["count"] == 0)

# --- detect_lao_script_thaiisms catches ໄຫມ ---
mai = detect_lao_script_thaiisms("ເຈົ້າໄປໄຫມ")
expect("ໄຫມ flagged", any(t["found"] == "ໄຫມ" for t in mai))

# --- check_file: detects leaks per line, clean file reports zero ---
with tempfile.TemporaryDirectory() as d:
    leaky = Path(d) / "leaky.html"
    leaky.write_text("<p>ກາເຟເຢັນ</p>\n<p>ນຸ່ມລະ" + "มุน" + "</p>\n", encoding="utf-8")
    lk, total = check_file(str(leaky))
    expect("check_file finds leak total", total == 3)
    expect("check_file reports line 2", lk[0][0] == 2)
    expect("check_file single leaky line", len(lk) == 1)

    clean = Path(d) / "clean.html"
    clean.write_text("<p>ກາເຟເຢັນ ສົດຊື່ນ</p>\n<button>ສັ່ງຊື້</button>\n", encoding="utf-8")
    lk2, total2 = check_file(str(clean))
    expect("check_file clean = 0", total2 == 0 and lk2 == [])

print(f"\n{_passed} passed, {_failed} failed")
sys.exit(1 if _failed else 0)
