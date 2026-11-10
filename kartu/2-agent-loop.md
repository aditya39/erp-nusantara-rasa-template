# Tahap 2 — Agent loop: menjawab "kenapa"

**Waktu:** 25 menit. **Hasil:** asisten menjawab dari data. Tombol **Telusuri penyebab** di halaman Analisis HPP sekarang mendapat jawaban.

Agent loop: model meminta tool → kode menjalankan → hasil dikirim balik ke model → diulang sampai model memberi jawaban. Pertanyaan "kenapa" biasanya butuh beberapa putaran.

## Prompt untuk Claude Code

```
Kerjakan Tahap 2 (kartu/2-agent-loop.md). Ikuti AGENTS.md, terutama bagian
"Kontrak agent" dan "Pengaman".

1. Ganti rintisan jalankan() di asisten/agent.py dengan agent loop. Pakai
   prompt.system_prompt(), llm.panggil(), tools.rapikan_argumen(), dan
   llm.pesan_hasil_tool(). Bentuk event mengikuti docstring di file itu.
   Sertakan SQL yang dijalankan tool di event tool (field "query", dari db.catat_query()).

2. Tambahkan tiga tool HPP di asisten/tools.py (izin "hpp"):
   - rincian_hpp(produk: str, bulan: str = "")
     HPP per unit bulan itu dibanding bulan sebelumnya, dirinci per bahan baku,
     tenaga kerja, dan overhead, diurutkan dari perubahan terbesar. Sertakan persen perubahan HPP.
   - riwayat_harga_bahan(bahan: str, bulan_terakhir: int = 6)
   - produk_pengguna_bahan(bahan: str)
     Produk yang memakai bahan itu dan porsi bahan tersebut dalam HPP-nya bulan terakhir.

Selesai kalau `python -m pytest tests/test_tahap1.py tests/test_tahap2.py -q` lulus.
Jangan mengerjakan tahap lain. Setelah selesai, tunjukkan di baris mana hasil tool
dikirim balik ke model dan di baris mana loop berhenti.
```

## Cek hasil

```bash
python scripts/cek_tahap.py          # Tahap 1 dan 2 ✓
python -m asisten --detail "Kenapa HPP Roti Cokelat naik bulan ini?"
```

Jalankan ulang ERP (`Ctrl+C` di terminal server, lalu `python -m server`). Login `budi`, buka **Produksi › Analisis HPP**, klik **Telusuri penyebab** (Roti Cokelat). Tombol yang sama ada di kartu "Perlu tindakan" di Ringkasan. Di panel, buka "Langkah agent" dan klik satu langkah untuk melihat query yang dijalankan dan hasil mentahnya.

Empat cek untuk setiap jawaban:

1. Tool yang dipilih masuk akal?
2. Argumennya benar (produk, bulan)?
3. Angka di jawaban sama dengan angka di hasil tool?
4. Periode datanya disebut?

## Pahami

1. Berapa kali model dipanggil untuk satu pertanyaan "kenapa"? Lihat jumlah token di bawah jawaban.
2. Siapa yang menghitung "+11,1%": model atau kode? Tunjukkan barisnya.
3. Login sebagai Andi, lalu tanya `Berapa HPP Roti Cokelat?`. Apa yang terjadi, dan baris kode mana yang menyebabkannya?

## Kalau macet

`python scripts/cek_tahap.py 2`, tempel pesan gagalnya ke Claude Code. Kalau waktu habis: `python scripts/pasang_kunci.py 2`.
