"""
Tahap 4 — RAG: potong dokumen, embedding, pencarian di pgvector, tool cari_dokumen.

  python -m asisten.rag ingest                 # sekali, setelah RAG_KOLEKSI diisi di .env
  python -m pytest tests/test_tahap4.py -q
"""
import pytest

from asisten import config, db, tools
from conftest import teks_json


@pytest.fixture(scope="module")
def rag():
    try:
        from asisten import rag as modul
    except ImportError:
        pytest.fail("asisten/rag.py belum ada")
    return modul


@pytest.fixture(scope="module")
def koleksi_siap(rag, butuh_db):
    assert config.RAG_KOLEKSI, "Isi RAG_KOLEKSI di .env dengan nama kelompok (huruf kecil, mis. kelompok_2)"
    ada = db.query("SELECT to_regclass(%(t)s) IS NOT NULL AS ada",
                   {"t": f"latihan.dokumen_{config.RAG_KOLEKSI}"})[0]["ada"]
    assert ada, "Koleksi dokumen belum dibuat. Jalankan: python -m asisten.rag ingest"


def test_dokumen_dipotong_per_bagian(rag):
    potongan = rag.potong_dokumen(config.FOLDER_DOKUMEN / "01-SOP-Retur-Barang.md")
    assert len(potongan) >= 3, "Dokumen dipotong per heading '##', bukan dijadikan satu potongan"
    for p in potongan:
        assert p["sumber"] and p["bagian"] and p["isi"], "Setiap potongan membawa sumber (judul dokumen), bagian, dan isi"
        assert len(p["isi"]) <= 2000, "Potongan terlalu panjang"
    assert "Retur" in potongan[0]["sumber"]


def test_semua_dokumen_masuk_koleksi(koleksi_siap):
    sumber = db.query(f'SELECT DISTINCT sumber FROM latihan."dokumen_{config.RAG_KOLEKSI}"')
    assert len(sumber) >= 6, "Keenam dokumen di folder dokumen/ harus masuk koleksi"


def test_pencarian_menemukan_dokumen_yang_tepat(rag, koleksi_siap):
    hasil = rag.cari("berapa lama batas waktu retur roti yang rusak", k=3)
    assert hasil and all(k in hasil[0] for k in ("sumber", "bagian", "isi", "skor"))
    assert any("Retur" in h["sumber"] for h in hasil), [h["sumber"] for h in hasil]
    hasil = rag.cari("jam berapa batas order supaya dikirim besok", k=3)
    assert any("Pengiriman" in h["sumber"] for h in hasil), [h["sumber"] for h in hasil]


def test_tool_cari_dokumen(koleksi_siap):
    assert "cari_dokumen" in tools.REGISTRY, "Tool cari_dokumen belum terdaftar"
    t = tools.REGISTRY["cari_dokumen"]
    assert t.izin == "dokumen"
    with db.catat_query() as query:
        hasil = t.fungsi(pertanyaan="diskon tambahan maksimal untuk sales supervisor")
    teks = teks_json(hasil)
    assert "Kebijakan Harga" in teks, "Hasil harus menyebut judul dokumen sumbernya"
    assert "KBJ-PJL-002" in teks, "Sertakan nomor dokumen, supaya jawaban bisa menyebut sumber dengan tepat"
    assert all("erp." not in q["sql"].lower() for q in query)


def test_agent_memakai_dokumen(model_palsu, koleksi_siap):
    from conftest import tanya
    model = model_palsu([("cari_dokumen", {"pertanyaan": "batas retur roti rusak"}), "Sesuai SOP Retur Barang."])
    ev = tanya("Berapa lama batas retur roti yang rusak?", pengguna="andi")
    assert next(e for e in ev if e["tipe"] == "tool")["status"] == "ok"
    assert "Retur" in model.pesan_tool()[0], "Potongan dokumen dikirim ke model sebagai hasil tool"
