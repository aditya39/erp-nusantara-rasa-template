#!/usr/bin/env python3
"""
Papan status tahap. Jalankan dari folder utama proyek:

    python scripts/cek_tahap.py          # semua tahap
    python scripts/cek_tahap.py 2        # satu tahap, dengan rincian tes yang gagal

✓ semua tes lulus · ✗ ada tes gagal (belum dibangun atau belum benar) · ? tidak bisa dicek (mis. database tidak terhubung)
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Windows: keluaran yang di-pipe (mis. saat dijalankan coding agent) tidak selalu UTF-8, padahal ada tanda seperti ✓.
for _aliran in (sys.stdout, sys.stderr):
    if hasattr(_aliran, "reconfigure"):
        _aliran.reconfigure(encoding="utf-8", errors="replace")
LINGKUNGAN = {**os.environ, "PYTHONIOENCODING": "utf-8"}
TAHAP = [
    ("1", "Tool penjualan"),
    ("2", "Agent loop + tool HPP                  "),
    ("3", "Pengaman + jejak audit"),
    ("4", "RAG dokumen SOP"),
    ("5a", "Fitur A: briefing pagi"),
    ("5b", "Fitur B: draft surat penagihan"),
    ("5c", "Fitur C: email jadi draft SO"),
]


def jalankan(kode: str, rinci: bool = False) -> tuple[str, str]:
    perintah = [sys.executable, "-m", "pytest", f"tests/test_tahap{kode}.py", "-q", "--no-header", "-p", "no:cacheprovider"]
    if not rinci:
        perintah.append("--tb=no")
    hasil = subprocess.run(perintah, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=LINGKUNGAN)
    keluaran = hasil.stdout + hasil.stderr
    ringkas = (re.findall(r"^(?:=+ )?(\d+ [a-z]+(?:, \d+ [a-z]+)*) in [\d.]+s", keluaran, flags=re.M) or [""])[-1]
    if hasil.returncode == 0 and "skipped" not in ringkas:
        return "✓", ringkas
    if hasil.returncode == 0 or ("skipped" in ringkas and "failed" not in ringkas and "error" not in ringkas):
        return "?", ringkas or "tes dilewati"
    return "✗", ringkas or keluaran.strip().splitlines()[-1] if keluaran.strip() else "gagal dijalankan"


def main() -> None:
    pilihan = [a.lower() for a in sys.argv[1:]]
    if pilihan:
        for kode in pilihan:
            if kode not in dict(TAHAP):
                sys.exit(f"Tahap '{kode}' tidak dikenal. Pilihan: {', '.join(k for k, _ in TAHAP)}")
            subprocess.run([sys.executable, "-m", "pytest", f"tests/test_tahap{kode}.py", "-q", "--no-header",
                            "-p", "no:cacheprovider"], cwd=ROOT, env=LINGKUNGAN)
        return
    print("Status tahap (tes penerimaan di folder tests/)\n")
    for kode, judul in TAHAP:
        tanda, ringkas = jalankan(kode)
        print(f" {tanda} Tahap {kode.upper():<3} {judul:<42} {ringkas}")
    print("\nRincian satu tahap: python scripts/cek_tahap.py 2")


if __name__ == "__main__":
    main()
