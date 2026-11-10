"""
Tahap 2 — agent loop dan tool HPP.

  python -m pytest tests/test_tahap2.py -q
"""
import pytest

from asisten import config, db, tools
from asisten import format as fmt
from conftest import tanya, teks_json


def tipe(events):
    return [e["tipe"] for e in events]


def test_loop_tool_lalu_jawaban(model_palsu, butuh_db):
    model = model_palsu([("tren_penjualan", {"produk": "Biskuit Kelapa", "bulan_terakhir": 3}), "Naik 36,4%."])
    ev = tanya()
    assert tipe(ev)[0] == "mulai" and tipe(ev)[-1] == "selesai"
    alat = [e for e in ev if e["tipe"] == "tool"]
    assert len(alat) == 1 and alat[0]["status"] == "ok" and alat[0]["nama"] == "tren_penjualan", \
        "Tool yang diminta model harus dijalankan kode (status 'ok'), bukan hanya ditampilkan"
    assert next(e for e in ev if e["tipe"] == "jawaban")["teks"] == "Naik 36,4%."
    assert len(model.dikirim) == 2, "Setelah tool dijalankan, model harus ditanya lagi dengan hasilnya"


def test_hasil_tool_dikirim_balik_ke_model(model_palsu, butuh_db):
    model = model_palsu([("tren_penjualan", {"produk": "Biskuit Kelapa", "bulan_terakhir": 3}), "Selesai."])
    tanya()
    hasil = model.pesan_tool()
    assert hasil and "Biskuit Kelapa 200g" in hasil[0], "Hasil tool dikirim ke model sebagai pesan role 'tool'"
    assert '"grafik"' not in hasil[0], "Field 'grafik' untuk layar saja, jangan dikirim ke model"


def test_beberapa_langkah(model_palsu, butuh_db):
    model_palsu([("rincian_hpp", {"produk": "Roti Cokelat"}),
                 ("riwayat_harga_bahan", {"bahan": "kakao bubuk"}),
                 ("produk_pengguna_bahan", {"bahan": "kakao bubuk"}),
                 "HPP naik karena kakao."])
    ev = tanya()
    alat = [e for e in ev if e["tipe"] == "tool"]
    assert [a["nama"] for a in alat] == ["rincian_hpp", "riwayat_harga_bahan", "produk_pengguna_bahan"]
    assert all(a["status"] == "ok" for a in alat), [a["hasil"] for a in alat if a["status"] != "ok"]
    assert next(e for e in ev if e["tipe"] == "jawaban")["teks"] == "HPP naik karena kakao."


def test_batas_langkah(model_palsu, butuh_db):
    model = model_palsu([("cari_produk", {"kata_kunci": "roti"})])   # model palsu yang tidak pernah berhenti
    ev = tanya()
    assert len(model.dikirim) <= config.MAKS_LANGKAH + 1, "Loop harus berhenti di MAKS_LANGKAH (asisten/config.py)"
    assert "jawaban" in tipe(ev) and tipe(ev)[-1] == "selesai", "Saat batas langkah tercapai, user tetap diberi jawaban"


def test_tool_tidak_dikenal_tidak_menggagalkan(model_palsu, butuh_db):
    model_palsu([("hapus_semua_data", {}), "Maaf, tidak bisa."])
    ev = tanya()
    alat = [e for e in ev if e["tipe"] == "tool"]
    assert alat and alat[0]["status"] == "error"
    assert tipe(ev)[-1] == "selesai"


def test_argumen_dari_model_dirapikan(model_palsu, butuh_db):
    model_palsu([("tren_penjualan", {"produk": "Biskuit Kelapa", "bulan_terakhir": "3", "asal": "ngarang"}), "Ok."])
    alat = next(e for e in tanya() if e["tipe"] == "tool")
    assert alat["status"] == "ok", "Model kecil kadang mengirim '3' untuk 3 atau argumen yang tidak ada: pakai tools.rapikan_argumen"


@pytest.mark.parametrize("nama", ["rincian_hpp", "riwayat_harga_bahan", "produk_pengguna_bahan"])
def test_tool_hpp_terdaftar(nama):
    assert nama in tools.REGISTRY, f"Tool '{nama}' belum terdaftar"
    assert tools.REGISTRY[nama].izin == "hpp"


def test_rincian_hpp_roti_cokelat(butuh_db):
    hasil = tools.REGISTRY["rincian_hpp"].fungsi(produk="roti cokelat")
    teks = teks_json(hasil)
    akhir = db.info()["bulan_terakhir"]
    baris = {b["bulan"]: b["hpp_per_unit"] for b in db.query(
        "SELECT bulan, hpp_per_unit FROM ai.v_hpp_bulanan WHERE produk = 'Roti Cokelat' AND bulan >= %(a)s",
        {"a": fmt.tambah_bulan(akhir, -1)})}
    ubah = fmt.ubah_persen(baris[fmt.tambah_bulan(akhir, -1).isoformat()], baris[akhir.isoformat()])
    assert fmt.persen(ubah) in teks or str(ubah) in teks, f"Perubahan HPP Roti Cokelat seharusnya {fmt.persen(ubah)}"
    assert "kakao" in teks.lower(), "Rincian per bahan harus menunjukkan komponen yang paling berubah (kakao bubuk)"


def test_produk_pengguna_bahan(butuh_db):
    hasil = tools.REGISTRY["produk_pengguna_bahan"].fungsi(bahan="kakao bubuk")
    assert "Roti Cokelat" in teks_json(hasil)
