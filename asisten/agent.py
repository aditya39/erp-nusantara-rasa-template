"""
Agent: penghubung antara pertanyaan user, model, dan tools.

jalankan() adalah generator yang mengeluarkan event, supaya layar bisa menampilkan
setiap langkah secara langsung. Bentuk event adalah KONTRAK dengan layar (web/static/app.js)
dan dengan tes penerimaan, jadi nama field-nya jangan diubah:

  {"tipe": "mulai",    "mode", "model", "pengguna"}
  {"tipe": "berpikir", "langkah"}                      model sedang diminta memutuskan
  {"tipe": "tool",     "langkah", "nama", "argumen", "status", "ringkas", "durasi_ms", "hasil",
                       "query" (opsional)}             status: ok / ditolak / error / diminta
  {"tipe": "grafik",   "grafik"}                       data grafik dari hasil tool (tidak dikirim ke model)
  {"tipe": "draft_so", "draft"}                        draft sales order (BELUM disimpan)
  {"tipe": "jawaban",  "teks"}                         jawaban akhir
  {"tipe": "error",    "pesan"}                        kegagalan (mis. model tidak dapat dihubungi)
  {"tipe": "selesai",  "durasi_ms", "token_masuk", "token_keluar"}   selalu event terakhir
"""
from __future__ import annotations

import time
from typing import Any, Iterator

import openai
import psycopg

from . import config, db, llm, pengguna, prompt, tools


def _pesan_error(e: Exception, mode: str, cfg: config.ModelConfig) -> str:
    if isinstance(e, openai.APITimeoutError):
        return (f"Model {mode} tidak menjawab dalam {config.MODEL_TIMEOUT:g} detik. "
                "Server model kemungkinan sedang sibuk; coba lagi sebentar lagi.")
    if isinstance(e, openai.APIConnectionError):
        return (f"Model {mode} tidak dapat dihubungi di {cfg.base_url}. "
                "Periksa LOKAL_BASE_URL di .env (server workshop) atau koneksi internet (cloud).")
    if isinstance(e, psycopg.OperationalError):
        return f"Database tidak dapat dihubungi: {str(e).splitlines()[0]}"
    return f"Model {mode} mengembalikan error: {e}"


_GAGAL = (openai.APIError, RuntimeError, psycopg.OperationalError)


def jalankan(pertanyaan: str, kode_pengguna: str = "budi", mode: str = "lokal",
             riwayat: list[dict] | None = None) -> Iterator[dict[str, Any]]:
    """
    RINTISAN dari template (Tahap 0 dan 1): model ditanya SATU kali, dan tool belum dijalankan.

    Kalau model meminta tool, permintaannya hanya ditampilkan (status "diminta").
    Di Tahap 2 fungsi ini diganti dengan agent loop: jalankan tool yang diminta,
    kirim hasilnya ke model, ulangi sampai model memberi jawaban akhir.
    """
    cfg = config.model_untuk(mode)
    u = pengguna.ambil(kode_pengguna)
    mulai = time.perf_counter()
    token_masuk = token_keluar = 0
    yield {"tipe": "mulai", "mode": mode, "model": cfg.model, "pengguna": u["nama"]}
    try:
        pesan = [{"role": "system", "content": prompt.prompt_polos(kode_pengguna)},
                 {"role": "user", "content": pertanyaan}]
        yield {"tipe": "berpikir", "langkah": 1}
        balasan = llm.panggil(cfg, pesan, tools.semua_skema())
        token_masuk, token_keluar = balasan.token_masuk, balasan.token_keluar
        for p in balasan.panggilan:
            yield {"tipe": "tool", "langkah": 1, "nama": p["nama"], "argumen": p["argumen"], "status": "diminta",
                   "ringkas": "diminta model, belum dijalankan", "durasi_ms": 0, "hasil": {}}
        if balasan.panggilan:
            teks = ("Model meminta tool di atas, tetapi belum ada kode yang menjalankannya. "
                    "Agent loop dibangun di Tahap 2.")
        else:
            teks = balasan.teks or "(model tidak memberi jawaban)"
        yield {"tipe": "jawaban", "teks": teks}
    except _GAGAL as e:
        yield {"tipe": "error", "pesan": _pesan_error(e, mode, cfg)}
    yield {"tipe": "selesai", "durasi_ms": int((time.perf_counter() - mulai) * 1000),
           "token_masuk": token_masuk, "token_keluar": token_keluar}
