"""
Tahap 5C — pesanan dari email menjadi draft sales order.
AI menyiapkan draft, sistem ERP menghitung, manusia menekan Simpan, kode aplikasi yang menyimpan.

  python -m pytest tests/test_tahap5c.py -q
"""
import re

from asisten import config, db, tools
from conftest import tanya

ITEM = [{"produk": "Roti Keju", "qty": 600}, {"produk": "Kopi Susu Botol 250ml", "qty": 400},
        {"produk": "Keripik Singkong Balado", "qty": 500}]


def draft():
    assert "siapkan_draft_so" in tools.REGISTRY, "Tool 'siapkan_draft_so' belum terdaftar (asisten/transaksi.py)"
    with db.catat_query() as query:
        hasil = tools.REGISTRY["siapkan_draft_so"].fungsi(customer="Swalayan Sentosa", item=ITEM,
                                                           catatan="PO-SS/2026/10/118")
    return hasil, query


def test_tool_terdaftar_dengan_izin_so_buat():
    assert "siapkan_draft_so" in tools.REGISTRY
    assert tools.REGISTRY["siapkan_draft_so"].izin == "so_buat"


def test_draft_berisi_customer_item_dan_payload(butuh_db):
    hasil, _ = draft()
    d = hasil.get("draft_so")
    assert isinstance(d, dict), f"Hasil harus berisi 'draft_so'. Dapat: {hasil}"
    assert d["customer"]["nama"] == "Swalayan Sentosa" and d["customer"]["id"]
    assert [i["qty"] for i in d["item"]] == [x["qty"] for x in ITEM]
    for i, x in zip(d["item"], ITEM):   # nama di draft adalah nama katalog, mis. "Keripik Singkong Balado 100g"
        assert i["nama"].startswith(x["produk"]), f"{x['produk']} dicocokkan ke {i['nama']}"
    assert all(i.get("harga_daftar_fmt") and i.get("satuan") and i.get("kode") for i in d["item"])
    assert d["gudang"] and d["nilai_bruto_fmt"] and "PO-SS/2026/10/118" in d["catatan"]
    p = d["payload"]
    assert p["customer_id"] == d["customer"]["id"] and p["gudang"] == d["gudang"]
    assert [(i["produk_id"], i["qty"]) for i in p["item"]] == [(i["produk_id"], i["qty"]) for i in d["item"]]


def test_tool_hanya_membaca(butuh_db):
    _, query = draft()
    assert query and all(q["sql"].lower().lstrip().startswith(("select", "with")) for q in query), \
        "siapkan_draft_so hanya boleh SELECT: draft tidak disimpan oleh tool"
    assert all("erp." not in q["sql"].lower() for q in query)


def test_model_tidak_punya_tool_untuk_menyimpan():
    terlarang = [n for n in tools.REGISTRY if re.search(r"simpan|buat_so|posting|insert|hapus|ubah", n)]
    assert not terlarang, f"Model tidak boleh punya tool yang menulis transaksi: {terlarang}"


def test_produk_ambigu_ditanyakan_balik(butuh_db):
    hasil = tools.REGISTRY["siapkan_draft_so"].fungsi(customer="Swalayan Sentosa", item=[{"produk": "biskuit", "qty": 10}])
    assert "draft_so" not in hasil and "error" in hasil, "Produk ambigu: jangan ditebak, kembalikan error + kandidat"


def test_agent_mengeluarkan_event_draft(model_palsu, butuh_db):
    model_palsu([("siapkan_draft_so", {"customer": "Swalayan Sentosa", "item": ITEM}), "Draft siap, mohon diperiksa."])
    ev = tanya("Siapkan draft SO dari email berikut ...", pengguna="andi")
    kartu = [e for e in ev if e["tipe"] == "draft_so"]
    assert len(kartu) == 1 and kartu[0]["draft"]["customer"]["nama"] == "Swalayan Sentosa", \
        "Agent mengeluarkan event {'tipe': 'draft_so', 'draft': ...} supaya layar menampilkan kartu draft"


def test_user_tanpa_izin_so_ditolak(model_palsu, butuh_db):
    model_palsu([("siapkan_draft_so", {"customer": "Swalayan Sentosa", "item": ITEM}), "Tidak ada akses."])
    ev = tanya(pengguna="sari")   # Finance tidak boleh membuat SO
    assert next(e for e in ev if e["tipe"] == "tool")["status"] == "ditolak"
    assert not [e for e in ev if e["tipe"] == "draft_so"]
