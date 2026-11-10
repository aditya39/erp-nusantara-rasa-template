"""
Tahap 3 — pengaman dan jejak audit.

  python -m pytest tests/test_tahap3.py -q
"""
import psycopg
import pytest

from asisten import db
from conftest import tanya, teks_json


def test_izin_dicek_kode_bukan_prompt(model_palsu, butuh_db):
    # andi (Sales Supervisor) tidak punya izin HPP. Model palsu "nekat" meminta tool HPP.
    model = model_palsu([("rincian_hpp", {"produk": "Roti Cokelat"}), "Tidak ada akses."])
    ev = tanya(pengguna="andi")
    alat = next(e for e in ev if e["tipe"] == "tool")
    assert alat["status"] == "ditolak", "Izin user harus dicek KODE sebelum tool dijalankan"
    assert not alat.get("query"), "Tool yang ditolak tidak boleh sempat menjalankan query"
    hasil = model.pesan_tool()[0]
    assert "AKSES_DITOLAK" in hasil, "Model diberi tahu AKSES_DITOLAK supaya bisa menjelaskan ke user"
    assert "hpp_per_unit" not in hasil and "Kakao" not in hasil, "Data HPP bocor ke model walau izin ditolak"


def test_user_berizin_tetap_bisa(model_palsu, butuh_db):
    model_palsu([("rincian_hpp", {"produk": "Roti Cokelat"}), "Naik."])
    assert next(e for e in tanya(pengguna="sari") if e["tipe"] == "tool")["status"] == "ok"


def test_koneksi_asisten_tidak_bisa_menulis(butuh_db):
    with pytest.raises(psycopg.Error):
        db.query("UPDATE erp.produk SET harga_jual = 1")
    with pytest.raises(psycopg.Error):
        db.query("SELECT * FROM erp.gaji_karyawan")


def test_setiap_pertanyaan_tercatat(model_palsu, butuh_db, tmp_path, monkeypatch):
    from asisten import audit
    monkeypatch.setattr(audit, "FILE_LOG", tmp_path / "aktivitas.jsonl")
    model_palsu([("rincian_hpp", {"produk": "Roti Cokelat"}), "Tidak ada akses."])
    tanya("Berapa HPP Roti Cokelat?", pengguna="andi")
    model_palsu([("tren_penjualan", {"produk": "Biskuit Kelapa"}), "Naik."])
    tanya("Tren Biskuit Kelapa?", pengguna="budi")
    catatan = audit.baca()
    assert len(catatan) == 2, "Setiap pertanyaan menambah satu catatan di log"
    terbaru, lama = catatan[0], catatan[1]
    assert terbaru["pengguna"] == "budi" and lama["pengguna"] == "andi", "audit.baca() mengembalikan yang terbaru lebih dulu"
    assert lama["pertanyaan"] == "Berapa HPP Roti Cokelat?" and lama.get("waktu")
    assert [(t["nama"], t["status"]) for t in lama["tools"]] == [("rincian_hpp", "ditolak")], \
        "Tool yang ditolak juga harus tercatat (nama dan status)"
    assert terbaru["tools"][0]["status"] == "ok"
    assert "Kakao" not in teks_json(catatan), "Log tidak menyimpan hasil tool"
