"""
Tanya asisten dari terminal (tanpa membuka layar ERP).

  python -m asisten "Bagaimana tren penjualan Biskuit Kelapa 3 bulan terakhir?"
  python -m asisten --pengguna andi "Berapa HPP Roti Cokelat bulan ini?"
  python -m asisten --mode cloud "..."
  python -m asisten --detail "..."      # tampilkan juga SQL dan hasil mentah setiap tool
"""
from __future__ import annotations

import argparse
import json
import sys

from . import agent, pengguna

# Windows: keluaran yang di-pipe (mis. saat dijalankan coding agent) tidak selalu UTF-8, padahal ada tanda seperti ✓.
for _aliran in (sys.stdout, sys.stderr):
    if hasattr(_aliran, "reconfigure"):
        _aliran.reconfigure(encoding="utf-8", errors="replace")

TANDA = {"ok": "✓", "ditolak": "✗ DITOLAK", "error": "✗ ERROR", "diminta": "… DIMINTA (belum dijalankan)"}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pertanyaan")
    ap.add_argument("--pengguna", default="budi", choices=list(pengguna.PENGGUNA))
    ap.add_argument("--mode", default="lokal", choices=["lokal", "cloud"])
    ap.add_argument("--detail", action="store_true")
    args = ap.parse_args()

    for ev in agent.jalankan(args.pertanyaan, args.pengguna, args.mode):
        t = ev["tipe"]
        if t == "mulai":
            print(f"» {ev['pengguna']} · model {ev['mode']} ({ev['model']})")
        elif t == "berpikir":
            print(f"  [{ev['langkah']}] model memutuskan…")
        elif t == "tool":
            print(f"      {TANDA.get(ev['status'], ev['status'])} {ev['nama']}"
                  f"({json.dumps(ev['argumen'], ensure_ascii=False)}) → {ev['ringkas']} · {ev.get('durasi_ms', 0)} ms")
            if args.detail:
                for q in ev.get("query", []):
                    print(f"        SQL: {q['sql']}"
                          + (f"  · params {json.dumps(q['params'], ensure_ascii=False, default=str)}" if q["params"] else ""))
                print("        " + json.dumps(ev["hasil"], ensure_ascii=False, indent=2).replace("\n", "\n        "))
        elif t == "draft_so":
            d = ev["draft"]
            print(f"      draft SO (BELUM disimpan): {d['customer']['nama']} · {d['gudang']} · "
                  + ", ".join(f"{x['qty']} {x['satuan']} {x['nama']}" for x in d["item"]))
        elif t == "grafik":
            print(f"      grafik: {ev['grafik'].get('judul', '')}")
        elif t == "jawaban":
            print("\n" + ev["teks"] + "\n")
        elif t == "error":
            print(f"\n[ERROR] {ev['pesan']}\n")
        elif t == "selesai":
            print(f"  selesai dalam {ev['durasi_ms'] / 1000:.1f} dtk · token masuk {ev['token_masuk']} "
                  f"· token keluar {ev['token_keluar']}")


if __name__ == "__main__":
    main()
