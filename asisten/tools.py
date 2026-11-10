"""
Tools yang boleh dipakai asisten AI.

Pola setiap tool:
  1. Deskripsi + skema parameter (JSON Schema) -> dibaca model untuk memilih tool.
  2. Izin yang dibutuhkan -> dicek oleh kode sebelum tool dijalankan.
  3. Fungsi Python yang menjalankan query BERPARAMETER ke view schema "ai".
  4. Hasil berisi angka yang sudah dihitung & diformat oleh kode (field *_fmt),
     sehingga model cukup menjelaskan, bukan menghitung.
  5. Field "grafik" (opsional) dikirim ke layar, tidak dikirim ke model.

Yang sudah ada dari template: registry, dekorator @tool, pencarian nama produk yang
toleran ejaan, dan SATU tool contoh (cari_produk). Tool lain dibangun per tahap.

View yang boleh dibaca (schema "ai"):
  ai.v_info         nama_perusahaan, tanggal_posisi
  ai.v_produk       id, kode, nama, kategori, satuan, harga_jual
  ai.v_customer     id, kode, nama, kota, segmen, termin_hari
  ai.v_penjualan    tanggal, bulan, nomor_faktur, customer_id, customer, kota, segmen,
                    produk_id, kode_produk, produk, kategori, qty, harga, diskon_persen, nilai
  ai.v_hpp_bulanan  bulan, produk_id, kode_produk, produk, unit_diproduksi, bahan_baku_per_unit,
                    tenaga_kerja_per_unit, overhead_per_unit, hpp_per_unit
  ai.v_hpp_komponen bulan, produk_id, produk, bahan_id, bahan, satuan, qty_per_unit, harga_bahan, biaya_per_unit
  ai.v_harga_bahan  bulan, bahan_id, kode, bahan, satuan, harga
  ai.v_piutang      faktur_id, nomor_faktur, tanggal, jatuh_tempo, customer_id, customer, kota, segmen,
                    total, terbayar, sisa, hari_lewat_jatuh_tempo
  ai.v_stok         produk_id, kode_produk, produk, gudang, qty, stok_minimum, di_bawah_minimum
Kolom "bulan" selalu tanggal 1 bulan itu (mis. 2026-10-01).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable

from . import db
from . import format as fmt


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
@dataclass
class Tool:
    nama: str
    deskripsi: str
    parameter: dict
    izin: str
    fungsi: Callable[..., dict]

    def skema(self) -> dict:
        """Format definisi tool untuk API Chat Completions (OpenAI-compatible)."""
        return {
            "type": "function",
            "function": {"name": self.nama, "description": self.deskripsi, "parameters": self.parameter},
        }


REGISTRY: dict[str, Tool] = {}


def tool(nama: str, deskripsi: str, parameter: dict, izin: str):
    """Dekorator untuk mendaftarkan fungsi sebagai tool."""
    def daftar(fungsi: Callable[..., dict]) -> Callable[..., dict]:
        REGISTRY[nama] = Tool(nama, deskripsi, parameter, izin, fungsi)
        return fungsi
    return daftar


def semua_skema() -> list[dict]:
    return [t.skema() for t in REGISTRY.values()]


def skema_untuk(izin_user: list[str]) -> list[dict]:
    """Alternatif: hanya tool yang diizinkan untuk user ini yang diperlihatkan ke model."""
    return [t.skema() for t in REGISTRY.values() if t.izin in izin_user]


# ---------------------------------------------------------------------------
# Merapikan argumen dari model (model kecil kadang mengirim '3' untuk 3, atau '2%' untuk 2)
# ---------------------------------------------------------------------------
def _pilih_enum(nilai: Any, pilihan: list) -> Any:
    """'Segmen' -> 'segmen', 'surabaya' -> 'Gudang Surabaya'. None bila tidak ada satu pilihan yang cocok."""
    rendah = str(nilai).strip().lower()
    cocok = [p for p in pilihan if str(p).lower() == rendah] or [p for p in pilihan if rendah and rendah in str(p).lower()]
    return cocok[0] if len(cocok) == 1 else None


def rapikan_argumen(skema: dict, argumen: dict) -> dict:
    """
    Buang argumen yang tidak ada di skema dan ubah tipe dasar sesuai skema.
    Panggil ini sebelum menjalankan fungsi tool: fungsi(**rapikan_argumen(tool.parameter, argumen)).
    Array dan object dibiarkan apa adanya; tool yang merapikan isinya.
    """
    props = skema.get("properties", {})
    hasil = {}
    for k, v in (argumen or {}).items():
        if k not in props or v is None:
            continue
        tipe = props[k].get("type")
        try:
            if tipe == "integer":
                v = int(float(v))
            elif tipe == "number":
                v = float(v.replace("%", "").replace(",", ".").strip()) if isinstance(v, str) else float(v)
            elif tipe == "string":
                v = str(v)
        except (TypeError, ValueError):
            continue
        if "enum" in props[k] and v not in props[k]["enum"]:
            v = _pilih_enum(v, props[k]["enum"])
            if v is None:
                continue
        hasil[k] = v
    return hasil


# ---------------------------------------------------------------------------
# Pencarian nama produk / bahan yang toleran ejaan
# ---------------------------------------------------------------------------
SINONIM = {"coklat": "cokelat", "choco": "cokelat", "chocolate": "cokelat", "tawar": "tawar",
           "biscuit": "biskuit", "biskut": "biskuit", "kripik": "keripik", "kopsus": "kopi susu"}
SINONIM_BAHAN = {"cokelat": "kakao", "coklat": "kakao", "cocoa": "kakao", "terigu": "tepung", "sawit": "minyak"}


def _kata(teks: str, sinonim: dict[str, str]) -> list[str]:
    teks = teks.lower()
    for a, b in sinonim.items():
        teks = re.sub(rf"\b{a}\b", b, teks)
    return [k for k in re.split(r"[^a-z0-9]+", teks) if len(k) > 1]


def _cocokkan(teks: str, kandidat: list[dict], sinonim: dict[str, str]) -> list[dict]:
    """Pilih kandidat yang paling banyak cocok kata-katanya dengan teks."""
    kata = _kata(teks, sinonim)
    if not kata:
        return []
    skor = []
    for k in kandidat:
        nama = " ".join(_kata(k["nama"], {})) + " " + k.get("kode", "").lower()
        s = sum(1 for w in kata if w in nama)
        if s:
            skor.append((s, k))
    if not skor:
        return []
    terbaik = max(s for s, _ in skor)
    return [k for s, k in skor if s == terbaik]


def _resolve_produk(teks: str) -> tuple[dict | None, dict | None]:
    """Kembalikan (produk, error). Error berisi saran bila tidak ketemu / ambigu."""
    semua = db.query("SELECT id, kode, nama, kategori, satuan, harga_jual FROM ai.v_produk ORDER BY nama")
    cocok = _cocokkan(teks, semua, SINONIM)
    if len(cocok) == 1:
        return cocok[0], None
    if not cocok:
        return None, {"error": f"Produk '{teks}' tidak ditemukan.",
                      "produk_tersedia": [p["nama"] for p in semua]}
    return None, {"error": f"Ada {len(cocok)} produk yang cocok dengan '{teks}'. Tanyakan ke user produk yang dimaksud.",
                  "kandidat": [p["nama"] for p in cocok]}


def _rentang_bulan(bulan_terakhir: int) -> tuple:
    bulan_terakhir = max(1, min(int(bulan_terakhir or 6), 18))
    akhir = db.info()["bulan_terakhir"]
    awal = fmt.tambah_bulan(akhir, -(bulan_terakhir - 1))
    return awal, akhir, bulan_terakhir


def _periode(awal, akhir) -> str:
    return fmt.bulan(akhir) if awal == akhir else f"{fmt.bulan(awal)} s.d. {fmt.bulan(akhir)}"


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
# Tool contoh dari template. Tiru polanya untuk tool lain.
@tool(
    nama="cari_produk",
    deskripsi="Mencari produk berdasarkan nama atau kode. Mengembalikan kode, nama, kategori, dan harga jual.",
    parameter={
        "type": "object",
        "properties": {
            "kata_kunci": {"type": "string", "description": "Nama atau kode produk, mis. 'roti cokelat'. Kosongkan untuk semua produk."},
        },
        "required": [],
    },
    izin="produk",
)
def cari_produk(kata_kunci: str = "") -> dict:
    semua = db.query("SELECT kode, nama, kategori, satuan, harga_jual FROM ai.v_produk ORDER BY kategori, nama")
    hasil = _cocokkan(kata_kunci, semua, SINONIM) if kata_kunci.strip() else semua
    for p in hasil:
        p["harga_jual_fmt"] = fmt.rupiah(p["harga_jual"])
    return {"jumlah": len(hasil), "produk": hasil}


# TAHAP 1: tool penjualan (tren_penjualan, penjualan_teratas) ditulis di bawah baris ini.


# Tool tambahan (fitur pilihan di Tahap 5) dimuat otomatis dari asisten/tools_tambahan.py.
from . import tools_tambahan  # noqa: F401,E402
