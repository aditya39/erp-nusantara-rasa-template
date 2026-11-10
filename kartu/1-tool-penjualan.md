# Tahap 1 — Tool pertama: data penjualan

**Waktu:** 20 menit. **Hasil:** model meminta tool yang tepat dengan argumen yang tepat.

Tool adalah fungsi biasa ditambah keterangan untuk model: nama, deskripsi, dan parameter. Model memilih tool hanya dari keterangan itu. Query-nya ditulis developer, bukan model.

## Prompt untuk Claude Code

```
Kerjakan Tahap 1 (kartu/1-tool-penjualan.md). Ikuti AGENTS.md.

Tambahkan dua tool di asisten/tools.py, meniru pola cari_produk:

1. tren_penjualan(produk: str = "", bulan_terakhir: int = 6)
   Penjualan per bulan (qty dan nilai rupiah) untuk satu produk selama N bulan terakhir,
   sampai bulan terakhir data. Kalau produk kosong, total semua produk.
   Field data: satu baris per bulan. Sertakan nama produk yang dikenali, periode,
   dan perubahan dari bulan pertama ke bulan terakhir (dihitung kode).

2. penjualan_teratas(dimensi: str = "produk", bulan_terakhir: int = 3, jumlah: int = 5)
   Peringkat nilai penjualan teratas menurut dimensi: produk, customer, kota, segmen, atau kategori.

Selesai kalau `python -m pytest tests/test_tahap1.py -q` lulus.
Jangan mengerjakan tahap lain. Setelah selesai, jelaskan query yang dijalankan tiap tool
dan bagaimana nilai dari model sampai ke query.
```

## Cek hasil

```bash
python scripts/cek_tahap.py          # Tahap 1 ✓
```

Jalankan ulang ERP (`Ctrl+C` di terminal server, lalu `python -m server`), login `andi`, lalu tanya di panel Asisten:

- `Bagaimana tren penjualan Biskuit Kelapa 3 bulan terakhir?`
- `Lima customer dengan penjualan terbesar 3 bulan terakhir?`

Yang seharusnya terlihat: baris "Langkah agent" berisi nama tool dan argumennya dengan tanda `…` (diminta, belum dijalankan). Belum ada jawaban berisi angka. Itu benar untuk tahap ini.

## Pahami

Jawab berdua dari kode yang baru ditulis:

1. Bagian mana dari tool yang dibaca model, dan bagian mana yang tidak pernah dilihat model?
2. Nama produk dari model masuk ke SQL lewat mana? Apa yang terjadi kalau model mengirim `'; DROP TABLE`?
3. Ubah deskripsi `penjualan_teratas` jadi satu kata saja, lalu tanya lagi. Apakah model masih memilihnya? Kembalikan setelah dicoba.

## Kalau macet

`python scripts/cek_tahap.py 1` menampilkan tes yang gagal dan alasannya. Tempel ke Claude Code. Kalau waktu habis: `python scripts/pasang_kunci.py 1`.
