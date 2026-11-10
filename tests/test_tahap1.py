"""
Tahap 1 — tool penjualan: tren_penjualan dan penjualan_teratas.

  python -m pytest tests/test_tahap1.py -q
"""
import json

import pytest

from asisten import db, tools
from asisten import format as fmt
from conftest import teks_json

PRODUK = "Biskuit Kelapa 200g"


def jalankan(nama, **kw):
    assert nama in tools.REGISTRY, f"Tool '{nama}' belum terdaftar. Tulis di asisten/tools.py dengan dekorator @tool."
    with db.catat_query() as query:
        hasil = tools.REGISTRY[nama].fungsi(**kw)
    assert isinstance(hasil, dict), "Hasil tool harus dict"
    return hasil, query


@pytest.mark.parametrize("nama", ["tren_penjualan", "penjualan_teratas"])
def test_tool_terdaftar_lengkap(nama):
    assert nama in tools.REGISTRY, f"Tool '{nama}' belum terdaftar di asisten/tools.py"
    t = tools.REGISTRY[nama]
    assert t.izin == "penjualan", "Tool penjualan harus memakai izin='penjualan'"
    assert len(t.deskripsi) >= 40, "Deskripsi terlalu pendek: jelaskan KAPAN model memakai tool ini"
    assert t.parameter["type"] == "object" and t.parameter.get("properties"), "Parameter harus JSON Schema object"
    json.dumps(t.skema())   # skema harus bisa dikirim ke model


def test_tren_penjualan_angkanya_dari_database(butuh_db):
    hasil, _ = jalankan("tren_penjualan", produk="biskuit kelapa", bulan_terakhir=3)
    teks = teks_json(hasil)
    assert PRODUK in teks, "Nama produk yang dikenali harus ikut di hasil (mis. 'Biskuit Kelapa 200g')"
    assert isinstance(hasil.get("data"), list) and len(hasil["data"]) == 3, "Field 'data' berisi satu baris per bulan"
    akhir = db.info()["bulan_terakhir"]
    acuan = db.query(
        "SELECT bulan, sum(qty) AS qty FROM ai.v_penjualan WHERE produk = %(p)s AND bulan >= %(a)s GROUP BY bulan",
        {"p": PRODUK, "a": fmt.tambah_bulan(akhir, -2)})
    assert len(acuan) == 3
    for b in acuan:
        assert str(b["qty"]) in teks or fmt.angka(b["qty"]) in teks, f"Qty {b['bulan']} ({b['qty']}) tidak ada di hasil tool"
    assert "_fmt" in teks, "Sertakan angka rupiah yang sudah diformat kode (field berakhiran _fmt)"


def test_query_berparameter_dan_hanya_view_ai(butuh_db):
    _, query = jalankan("tren_penjualan", produk="biskuit kelapa", bulan_terakhir=3)
    assert query, "Tool harus membaca database lewat db.query()"
    for q in query:
        sql = q["sql"].lower()
        assert "biskuit" not in sql, "Nilai dari model tidak boleh digabung ke teks SQL; pakai parameter %(nama)s"
        assert "erp." not in sql, "Tool hanya boleh membaca view schema ai, bukan tabel erp"
        assert sql.lstrip().startswith(("select", "with")), "Tool hanya boleh SELECT"
    assert any(q["params"] for q in query), "Query harus memakai parameter"


def test_produk_tidak_dikenal_tidak_membuat_error(butuh_db):
    hasil, _ = jalankan("tren_penjualan", produk="nastar nanas premium")
    assert "error" in hasil or not hasil.get("data"), "Produk yang tidak ada: kembalikan pesan, jangan data produk lain"


def test_penjualan_teratas_customer(butuh_db):
    hasil, _ = jalankan("penjualan_teratas", dimensi="customer", bulan_terakhir=3, jumlah=5)
    assert isinstance(hasil.get("data"), list) and len(hasil["data"]) == 5
    akhir = db.info()["bulan_terakhir"]
    acuan = db.query(
        """SELECT customer, sum(nilai) AS nilai FROM ai.v_penjualan WHERE bulan >= %(a)s
           GROUP BY customer ORDER BY nilai DESC LIMIT 1""", {"a": fmt.tambah_bulan(akhir, -2)})[0]
    assert acuan["customer"] in teks_json(hasil["data"][0]), f"Peringkat 1 seharusnya {acuan['customer']}"


def test_jumlah_baris_dibatasi(butuh_db):
    hasil, _ = jalankan("penjualan_teratas", dimensi="customer", bulan_terakhir=6, jumlah=500)
    assert len(hasil["data"]) <= 20, "Jumlah baris dibatasi maksimal 20, berapa pun yang diminta model"
