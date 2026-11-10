"""
Tool untuk fitur pilihan (Tahap 5). Tool yang ditulis di sini otomatis terdaftar
dan langsung bisa dipakai asisten di terminal maupun di layar ERP.

Pola lengkapnya ada di asisten/tools.py (lihat cari_produk). Daftar view dan kolomnya
ada di bagian atas file itu.
"""
from __future__ import annotations

from . import db
from . import format as fmt
from .tools import _cocokkan, tool  # noqa: F401
