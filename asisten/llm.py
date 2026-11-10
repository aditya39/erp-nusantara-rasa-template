"""
Klien model bahasa. Lokal (Ollama) dan cloud memakai API yang sama: OpenAI Chat Completions.

Yang dipakai kode agent:
  panggil(cfg, pesan, daftar_tool)  -> Balasan   satu kali bertanya ke model
  pesan_hasil_tool(id, hasil)       -> dict      pesan role "tool" untuk dikirim balik ke model

Kebiasaan model kecil sudah dirapikan di sini, supaya agent loop tetap sederhana:
  - blok <think>...</think> dibuang dari jawaban,
  - panggilan tool yang ditulis sebagai teks JSON tetap dikenali,
  - argumen tool selalu berupa dict (JSON rusak menjadi {}).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from openai import OpenAI

from . import config
from .config import ModelConfig


def buat_klien(cfg: ModelConfig) -> OpenAI:
    if not cfg.aktif:
        raise RuntimeError(f"Model {cfg.mode} belum dikonfigurasi (lihat .env.example).")
    return OpenAI(base_url=cfg.base_url, api_key=cfg.api_key or "kosong",
                  timeout=config.MODEL_TIMEOUT, max_retries=config.MODEL_COBA_ULANG)


def opsi_tambahan(cfg: ModelConfig) -> dict:
    """Parameter khusus penyedia. reasoning_effort='none' mematikan mode berpikir Qwen3 di Ollama."""
    return {"reasoning_effort": cfg.reasoning_effort} if cfg.reasoning_effort else {}


@dataclass
class Balasan:
    """Satu balasan model: jawaban teks ATAU permintaan memanggil tool (bisa lebih dari satu)."""
    teks: str                                   # jawaban model, sudah bersih dari <think>
    panggilan: list[dict] = field(default_factory=list)   # [{"id", "nama", "argumen": dict}]
    pesan: dict = field(default_factory=dict)   # pesan role "assistant", tambahkan ke daftar pesan apa adanya
    token_masuk: int = 0
    token_keluar: int = 0


def _bersihkan(teks: str | None) -> str:
    return re.sub(r"<think>.*?</think>", "", teks or "", flags=re.S).strip()


def _panggilan_dari_teks(teks: str, nama_tool: set[str]) -> list[dict]:
    """Model kecil kadang menulis {"name": ..., "arguments": {...}} sebagai teks biasa."""
    hasil = []
    for cocok in re.finditer(r'\{\s*"name"\s*:\s*"(\w+)"\s*,\s*"arguments"\s*:\s*', teks):
        if cocok.group(1) not in nama_tool:
            continue
        try:
            argumen, _ = json.JSONDecoder().raw_decode(teks, cocok.end())
        except json.JSONDecodeError:
            continue
        if isinstance(argumen, dict):
            hasil.append({"id": f"teks_{len(hasil) + 1}", "nama": cocok.group(1), "argumen": argumen})
    return hasil


def panggil(cfg: ModelConfig, pesan: list[dict], daftar_tool: list[dict] | None = None,
            klien: OpenAI | None = None) -> Balasan:
    """
    Kirim daftar pesan (dan skema tool, bila ada) ke model, lalu kembalikan Balasan.

    Model TIDAK menjalankan tool. Ia hanya mengembalikan nama tool dan argumennya
    (Balasan.panggilan); menjalankan tool adalah tugas kode kita.
    """
    klien = klien or buat_klien(cfg)
    opsi: dict = {"model": cfg.model, "messages": pesan, **opsi_tambahan(cfg)}
    if daftar_tool:
        opsi["tools"] = daftar_tool
    if cfg.suhu is not None:    # sebagian model (mis. Claude terbaru) menolak temperature di bawah 1
        opsi["temperature"] = cfg.suhu
    resp = klien.chat.completions.create(**opsi)
    msg = resp.choices[0].message

    panggilan = []
    for tc in (msg.tool_calls or []):
        try:
            argumen = json.loads(tc.function.arguments or "{}") or {}
        except json.JSONDecodeError:
            argumen = {}
        panggilan.append({"id": tc.id, "nama": tc.function.name, "argumen": argumen if isinstance(argumen, dict) else {}})
    if not panggilan and daftar_tool:
        panggilan = _panggilan_dari_teks(msg.content or "", {t["function"]["name"] for t in daftar_tool})

    teks = _bersihkan(msg.content)
    pesan_asisten: dict = {"role": "assistant", "content": teks}
    if panggilan:
        pesan_asisten = {
            "role": "assistant",
            "content": teks if msg.tool_calls else "",
            "tool_calls": [{"id": p["id"], "type": "function",
                            "function": {"name": p["nama"], "arguments": json.dumps(p["argumen"], ensure_ascii=False)}}
                           for p in panggilan],
        }
    pakai = getattr(resp, "usage", None)
    return Balasan(teks=teks, panggilan=panggilan, pesan=pesan_asisten,
                   token_masuk=(getattr(pakai, "prompt_tokens", 0) or 0) if pakai else 0,
                   token_keluar=(getattr(pakai, "completion_tokens", 0) or 0) if pakai else 0)


def pesan_hasil_tool(id_panggilan: str, hasil: dict) -> dict:
    """Pesan role "tool": hasil tool dikirim balik ke model sebagai JSON."""
    return {"role": "tool", "tool_call_id": id_panggilan,
            "content": json.dumps(hasil, ensure_ascii=False, default=str)}
