# Tahap 4 — RAG: asisten membaca dokumen SOP

**Waktu:** 17 menit. **Hasil:** asisten menjawab aturan dari dokumen dan menyebut sumbernya.

Data transaksi dijawab dengan tool dan query. Aturan dan prosedur ada di dokumen, jadi caranya lain: dokumen dipotong, tiap potongan diubah jadi vektor (embedding), lalu disimpan. Saat ada pertanyaan, potongan yang paling mirip diambil dan diberikan ke model.

## Sebelum mulai

Isi `RAG_KOLEKSI` di `.env` dengan nama unik untuk pasangan kalian (huruf kecil, tanpa spasi), misalnya `budi_sari`. Kalau baris `RAG_KOLEKSI=` muncul dua kali di `.env`, yang terbaca adalah yang paling bawah. Setiap pasangan punya tabelnya sendiri: `latihan.dokumen_<nama>`.

## Prompt untuk Claude Code

```
Kerjakan Tahap 4 (kartu/4-rag.md). Ikuti AGENTS.md.

1. Buat asisten/rag.py:
   - potong_dokumen(path) -> list[dict]: potong file Markdown per heading "##". Bagian yang lebih
     dari ±1.200 karakter dipecah per paragraf. Setiap potongan: sumber (judul dokumen dari baris "# "),
     nomor (dari baris "Nomor dokumen: ..."), bagian, isi.
   - embed(teks: list[str]) -> list[list[float]]: klien OpenAI ke config.EMBED_BASE_URL,
     model config.EMBED_MODEL, api_key config.EMBED_API_KEY.
   - ingest(folder=config.FOLDER_DOKUMEN) -> int: simpan semua potongan ke tabel
     latihan.dokumen_<config.RAG_KOLEKSI> (kolom sumber, nomor, bagian, isi, embedding vector).
     Koneksi: config.DATABASE_URL_PESERTA, atau DATABASE_URL_ADMIN kalau kosong. Tabel lama diganti.
     Setelah mengisi: buat index hnsw (vector_cosine_ops) dan GRANT SELECT ke erp_ai_readonly.
     Nama koleksi divalidasi: huruf kecil, angka, garis bawah, diawali huruf, maksimal 30 karakter.
   - cari(pertanyaan, k=4) -> list[dict]: sumber, nomor, bagian, isi, skor (1 - jarak cosine),
     lewat db.query() (koneksi read-only). ValueError yang jelas kalau koleksi belum dibuat.
   - CLI: python -m asisten.rag ingest | cari "pertanyaan"
2. Tambahkan tool cari_dokumen(pertanyaan: str) di asisten/tools.py (izin "dokumen").
   Hasilnya menyertakan judul dan nomor dokumen tiap potongan.
3. Jalankan ingest, lalu tes.

Selesai kalau `python scripts/cek_tahap.py` menunjukkan Tahap 1 sampai 4 lulus.
Jangan mengerjakan tahap lain.
```

## Cek hasil

```bash
python -m asisten.rag cari "batas retur roti yang rusak"     # tanpa model: potongan mana yang terambil?
python scripts/cek_tahap.py                                   # Tahap 4 ✓
```

Jalankan ulang ERP (`Ctrl+C` di terminal server, lalu `python -m server`), lalu tanya di panel Asisten:

- `Berapa lama batas retur untuk roti yang rusak?`
- `Berapa diskon tambahan yang boleh diberikan Sales Supervisor?`
- `Kenapa HPP Roti Cokelat naik, dan apa kata panduan soal kenaikan sebesar itu?` (data + dokumen dalam satu pertanyaan)

Buka "Langkah agent": potongan mana yang diambil, dari dokumen apa, dan berapa skornya.

## Pahami

1. Kenapa dokumen dipotong per bagian, bukan dikirim utuh ke model?
2. Tanya `Berapa total penjualan bulan lalu menurut dokumen?`. Apa yang terjadi? RAG bukan untuk angka transaksi.
3. Buka `dokumen-uji/Catatan-Pemasok-Mencurigakan.md`. Apa risikonya kalau dokumen seperti ini ikut di-ingest?

## Kalau macet

`python scripts/cek_tahap.py 4`. Kalau waktu habis: `python scripts/pasang_kunci.py 4`, lalu `python -m asisten.rag ingest`.
