"""
Tahap 5B — draft surat penagihan: tool piutang_customer + tombol di halaman Keuangan.
Butuh Tahap 4 (cari_dokumen) untuk kutipan kebijakan penagihan.

  python -m pytest tests/test_tahap5b.py -q
"""
from asisten import config, db, tools
from conftest import tanya, teks_json


def test_tool_terdaftar():
    assert "piutang_customer" in tools.REGISTRY, "Tool 'piutang_customer' belum terdaftar (asisten/tools_tambahan.py)"
    t = tools.REGISTRY["piutang_customer"]
    assert t.izin == "piutang" and "customer" in t.parameter["properties"]
    assert "cari_dokumen" in tools.REGISTRY, "Surat penagihan mengutip kebijakan: selesaikan Tahap 4 (RAG) dulu"


def test_rincian_faktur_customer(butuh_db):
    acuan = db.query("""SELECT customer, count(*) AS n, sum(sisa) AS sisa, max(hari_lewat_jatuh_tempo) AS hari
                        FROM ai.v_piutang GROUP BY customer ORDER BY sisa DESC LIMIT 1""")[0]
    hasil = tools.REGISTRY["piutang_customer"].fungsi(customer=acuan["customer"])
    assert isinstance(hasil.get("data"), list) and len(hasil["data"]) == acuan["n"], "Satu baris per faktur yang belum lunas"
    teks = teks_json(hasil)
    assert "nomor_faktur" in teks and str(acuan["hari"]) in teks, "Sertakan nomor faktur dan hari lewat jatuh tempo"
    assert "_fmt" in teks


def test_customer_tidak_dikenal(butuh_db):
    hasil = tools.REGISTRY["piutang_customer"].fungsi(customer="PT Tidak Pernah Ada")
    assert "error" in hasil or not hasil.get("data")


def test_user_tanpa_izin_piutang_ditolak(model_palsu, butuh_db):
    model_palsu([("piutang_customer", {"customer": "CV Laju Makmur Abadi"}), "Tidak ada akses."])
    assert next(e for e in tanya(pengguna="andi") if e["tipe"] == "tool")["status"] == "ditolak"
