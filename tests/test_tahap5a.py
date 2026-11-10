"""
Tahap 5A — briefing pagi: tool stok, piutang, dan margin + tombol di Dashboard.

  python -m pytest tests/test_tahap5a.py -q
"""
import pytest

from asisten import config, db, tools
from conftest import tanya, teks_json

IZIN = {"stok_di_bawah_minimum": "stok", "piutang_terbesar": "piutang", "margin_produk": "hpp"}


@pytest.mark.parametrize("nama", list(IZIN))
def test_tool_terdaftar_dengan_izin_yang_tepat(nama):
    assert nama in tools.REGISTRY, f"Tool '{nama}' belum terdaftar (tulis di asisten/tools_tambahan.py)"
    assert tools.REGISTRY[nama].izin == IZIN[nama]
    assert len(tools.REGISTRY[nama].deskripsi) >= 40


def test_stok_di_bawah_minimum(butuh_db):
    hasil = tools.REGISTRY["stok_di_bawah_minimum"].fungsi(jumlah=5)
    acuan = db.query("""SELECT produk, gudang FROM ai.v_stok WHERE di_bawah_minimum
                        ORDER BY stok_minimum - qty DESC LIMIT 1""")
    assert isinstance(hasil.get("data"), list) and 0 < len(hasil["data"]) <= 5
    assert acuan[0]["produk"] in teks_json(hasil["data"][0]), "Urutkan dari kekurangan terbesar"


def test_piutang_terbesar(butuh_db):
    hasil = tools.REGISTRY["piutang_terbesar"].fungsi(jumlah=3)
    acuan = db.query("SELECT customer, sum(sisa) AS sisa FROM ai.v_piutang GROUP BY customer ORDER BY sisa DESC LIMIT 1")[0]
    assert len(hasil["data"]) == 3 and acuan["customer"] in teks_json(hasil["data"][0])
    assert "_fmt" in teks_json(hasil), "Sertakan rupiah yang sudah diformat kode"


def test_margin_produk(butuh_db):
    hasil = tools.REGISTRY["margin_produk"].fungsi(jumlah=3)
    acuan = db.query(
        """SELECT h.produk FROM ai.v_hpp_bulanan h JOIN ai.v_produk p ON p.id = h.produk_id
           WHERE h.bulan = (SELECT date_trunc('month', tanggal_posisi)::date FROM ai.v_info)
           ORDER BY (p.harga_jual - h.hpp_per_unit) / p.harga_jual LIMIT 1""")[0]
    assert acuan["produk"] in teks_json(hasil["data"][0]), "Urutkan dari margin paling tipis"


def test_izin_tetap_berlaku_per_tool(model_palsu, butuh_db):
    # andi punya izin stok, tetapi tidak punya izin piutang dan HPP.
    model_palsu([("stok_di_bawah_minimum", {}), ("piutang_terbesar", {}), ("margin_produk", {}), "Ringkasan."])
    status = {e["nama"]: e["status"] for e in tanya(pengguna="andi") if e["tipe"] == "tool"}
    assert status == {"stok_di_bawah_minimum": "ok", "piutang_terbesar": "ditolak", "margin_produk": "ditolak"}
