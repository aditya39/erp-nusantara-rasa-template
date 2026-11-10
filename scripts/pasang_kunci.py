#!/usr/bin/env python3
"""
Pasang kunci jawaban satu tahap, kalau kelompok macet dan perlu lanjut ke tahap berikutnya.

    python scripts/pasang_kunci.py --daftar   # lihat isi kunci
    python scripts/pasang_kunci.py 2          # hasil jadi sampai Tahap 2
    python scripts/pasang_kunci.py 5c         # sampai Tahap 4 + fitur C
    python scripts/pasang_kunci.py jadi       # semua tahap + ketiga fitur

File yang ditimpa disalin dulu ke cadangan/<waktu>/, jadi pekerjaan kalian tidak hilang.
Kunci 5a, 5b, dan 5c masing-masing hanya berisi satu fitur. Untuk ketiganya sekaligus pakai "jadi".
"""
from __future__ import annotations

import datetime as dt
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KUNCI = ROOT / "kunci.zip"

# Windows: keluaran yang di-pipe (mis. saat dijalankan coding agent) tidak selalu UTF-8, padahal ada tanda seperti ✓.
for _aliran in (sys.stdout, sys.stderr):
    if hasattr(_aliran, "reconfigure"):
        _aliran.reconfigure(encoding="utf-8", errors="replace")


def main() -> None:
    if not KUNCI.exists():
        sys.exit("kunci.zip tidak ada di folder proyek. Minta ke mentor.")
    with zipfile.ZipFile(KUNCI) as z:
        tahap = sorted({n.split("/")[0].removeprefix("tahap-") for n in z.namelist() if "/" in n})
        if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
            sys.exit(__doc__)
        if sys.argv[1] == "--daftar":
            for t in tahap:
                print(f"tahap {t}: " + ", ".join(n.split("/", 1)[1] for n in z.namelist()
                                                 if n.startswith(f"tahap-{t}/") and not n.endswith("/")))
            return
        pilih = sys.argv[1].lower()
        if pilih not in tahap:
            sys.exit(f"Kunci '{pilih}' tidak ada. Pilihan: {', '.join(tahap)}")
        awalan = f"tahap-{pilih}/"
        anggota = [n for n in z.namelist() if n.startswith(awalan) and not n.endswith("/")]
        cadangan = ROOT / "cadangan" / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        for n in anggota:
            tujuan = ROOT / n[len(awalan):]
            if tujuan.exists():
                (cadangan / n[len(awalan):]).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(tujuan, cadangan / n[len(awalan):])
            tujuan.parent.mkdir(parents=True, exist_ok=True)
            tujuan.write_bytes(z.read(n))
            print(f"  dipasang: {n[len(awalan):]}")
    print(f"\nKunci tahap {pilih} terpasang. File lama ada di {cadangan.relative_to(ROOT)}/")
    print("Jalankan ulang ERP (Ctrl+C, lalu `python -m server`) supaya perubahan terbaca, lalu `python scripts/cek_tahap.py`.")
    if pilih in ("4", "5a", "5b", "5c", "jadi"):
        print("Tahap 4 butuh koleksi dokumen: isi RAG_KOLEKSI di .env, lalu `python -m asisten.rag ingest`.")


if __name__ == "__main__":
    main()
