# Tahap 0 — Kenali template

**Waktu:** 10 menit. **Belum ada yang dibangun di tahap ini.**

## Jalankan

```bash
docker compose ps                # db: healthy (kalau belum jalan: docker compose up -d)
python scripts/cek_setup.py      # semua baris ✓
python -m server                 # buka http://localhost:8080
```

Login sebagai `budi`, password `demo123`. Lihat-lihat dulu menunya: Ringkasan, Penjualan, Keuangan, Persediaan, Produksi (termasuk Analisis HPP), SOP & Kebijakan. Logout, lalu login sebagai `andi` dan `sari` (password sama): menu mana yang tertutup untuk Andi?

Tombol **Asisten** di kanan atas membuka panel Asisten. Tampilannya sudah jadi. Otaknya (paket `asisten/`) yang kalian bangun.

## Coba tanya asisten

Di panel Asisten, coba dua pertanyaan ini:

1. `Berapa penjualan Biskuit Kelapa bulan lalu?`
2. `Cari produk roti`

Catat apa yang terjadi:

- Di pertanyaan 1, model kadang mengarang angka dan kadang mengaku tidak punya akses. Artinya sama: model tidak tahu data perusahaan. Kalau ada angka, bandingkan dengan Laporan penjualan.
- Di pertanyaan 2, model **meminta** tool `cari_produk`, tetapi tidak ada yang menjalankannya. Model hanya bisa meminta. Yang menjalankan query nanti adalah kode kalian.

## Lihat kodenya (5 menit, bagi dua)

| Buka | Cari |
|---|---|
| `asisten/agent.py` | fungsi `jalankan()`: berapa kali model ditanya? |
| `asisten/tools.py` | tool `cari_produk`: deskripsi, parameter, izin, query |
| `server/routers/ai.py` | endpoint `/api/ai/chat` yang dipanggil panel: menyalin hak akses user ERP ke agent, memanggil `agent.jalankan()`, mencatat log. Sudah jadi, tidak diubah |
| `AGENTS.md` | aturan yang akan diikuti Claude Code di proyek ini |

Setelah itu buka Claude Code di folder ini (`claude`) dan lanjut ke Tahap 1.
