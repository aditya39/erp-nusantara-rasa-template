#!/usr/bin/env python3
"""
Cek kesiapan laptop. Jalankan dari folder utama proyek:

    python scripts/cek_setup.py

Baris ✓ dan ✗ wajib beres sebelum mulai. Baris • hanya informasi.
"""
from __future__ import annotations

import importlib
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
masalah = 0

# Windows: keluaran yang di-pipe (mis. saat dijalankan coding agent) tidak selalu UTF-8, padahal ada tanda seperti ✓.
for _aliran in (sys.stdout, sys.stderr):
    if hasattr(_aliran, "reconfigure"):
        _aliran.reconfigure(encoding="utf-8", errors="replace")


def lapor(tanda: str, teks: str, saran: str = "") -> None:
    global masalah
    masalah += tanda == "✗"
    print(f" {tanda} {teks}" + (f"\n     → {saran}" if saran else ""))


def ringkas(e: Exception) -> str:
    return " ".join(str(e).split())[:140]


print("Cek setup ERP Nusantara Rasa (template AI)\n")
v = sys.version_info
lapor("✓" if v >= (3, 10) else "✗", f"Python {v.major}.{v.minor}.{v.micro}", "" if v >= (3, 10) else "Butuh Python 3.10 atau lebih baru")
for paket in ("openai", "psycopg", "fastapi", "uvicorn", "dotenv", "pytest"):
    try:
        importlib.import_module(paket)
        lapor("✓", f"Paket {paket}")
    except ImportError:
        lapor("✗", f"Paket {paket} belum terpasang", "Aktifkan venv, lalu: pip install -r requirements.txt")
if masalah:
    sys.exit("\nPasang dulu Python dan paketnya, lalu jalankan lagi.")

if not (ROOT / ".env").exists():
    lapor("✗", "File .env belum ada", "Salin .env.example menjadi .env, lalu tempel blok PROFIL (d) dan isi API key dari mentor")
from asisten import config  # noqa: E402

lapor("•", f"Model chat: {config.LOKAL.model} di {config.LOKAL.base_url}")

import psycopg  # noqa: E402

try:
    with psycopg.connect(config.DATABASE_URL, connect_timeout=5) as conn:
        nama, posisi = conn.execute("SELECT nama_perusahaan, tanggal_posisi FROM ai.v_info").fetchone()
    lapor("✓", f"Database (role read-only): {nama}, posisi data {posisi}")
except psycopg.Error as e:
    lapor("✗", f"Database tidak dapat dihubungi ({ringkas(e)})", "Database lokal belum jalan? Jalankan: docker compose up -d, lalu docker compose ps (harus healthy)")

from openai import OpenAI  # noqa: E402

try:
    from asisten import llm
    t0 = time.perf_counter()
    balasan = llm.panggil(config.LOKAL, [{"role": "user", "content": "Jawab satu kata: siap"}])
    lapor("✓", f"Model chat menjawab dalam {time.perf_counter() - t0:.1f} dtk: {balasan.teks[:40]!r}")
except Exception as e:  # noqa: BLE001
    lapor("✗", f"Model chat gagal ({ringkas(e)})", "Cek LOKAL_BASE_URL, LOKAL_MODEL, dan LOKAL_API_KEY di .env (blok PROFIL (d)), dan koneksi internet")

try:
    klien = OpenAI(base_url=config.EMBED_BASE_URL, api_key=config.EMBED_API_KEY, timeout=30)
    dimensi = len(klien.embeddings.create(model=config.EMBED_MODEL, input=["uji"]).data[0].embedding)
    lapor("✓", f"Embedding {config.EMBED_MODEL}: {dimensi} dimensi")
except Exception as e:  # noqa: BLE001
    lapor("✗", f"Embedding gagal di {config.EMBED_BASE_URL} ({ringkas(e)})",
          "Ollama sudah jalan dan modelnya ada? ollama list (harus ada bge-m3), kalau belum: ollama pull bge-m3. Dibutuhkan mulai Tahap 4")

if config.RAG_KOLEKSI:
    lapor("•", f"Koleksi dokumen: latihan.dokumen_{config.RAG_KOLEKSI}")
else:
    lapor("•", "RAG_KOLEKSI belum diisi (dibutuhkan di Tahap 4: huruf kecil, mis. budi)")
if config.DATABASE_URL_PESERTA:
    try:
        psycopg.connect(config.DATABASE_URL_PESERTA, connect_timeout=5).close()
        lapor("✓", "Koneksi ingest dokumen (role peserta)")
    except psycopg.Error as e:
        lapor("✗", f"Koneksi ingest dokumen gagal ({ringkas(e)})", "Cek DATABASE_URL_PESERTA di .env")
else:
    lapor("•", "DATABASE_URL_PESERTA kosong: ingest dokumen memakai koneksi admin lokal (mode laptop sendiri)")

try:
    import urllib.request
    urllib.request.urlopen(config.ERP_URL + "/api/auth/akun-demo", timeout=5).read()
    lapor("•", f"ERP sudah berjalan di {config.ERP_URL}")
except Exception:  # noqa: BLE001
    lapor("•", f"ERP belum berjalan di {config.ERP_URL} (jalankan: python -m server)")

print(f"\nSemua siap. Lanjut: python -m server, lalu buka {config.ERP_URL}" if not masalah else f"\n{masalah} hal perlu dibereskan dulu.")
sys.exit(1 if masalah else 0)
