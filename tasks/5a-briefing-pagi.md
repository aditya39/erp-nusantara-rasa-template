# Tahap 5A — Briefing pagi

**Waktu:** 22 menit. **Hasil:** asisten bisa merangkum hal yang perlu ditindak hari ini: stok, piutang, dan margin.

**Untuk siapa di klien:** direktur operasional atau manajer yang setiap pagi membuka tiga laporan berbeda.
**Pola:** agent dengan beberapa tool baca. Risikonya rendah karena tidak ada yang ditulis.

## Prompt untuk Claude Code

```
Kerjakan Tahap 5A (tasks/5a-briefing-pagi.md). Ikuti AGENTS.md.

1. Tambahkan tiga tool di asisten/tools_tambahan.py:
   - stok_di_bawah_minimum(jumlah: int = 5), izin "stok":
     produk yang stoknya di bawah stok minimum per gudang, dari kekurangan terbesar.
   - piutang_terbesar(jumlah: int = 5, min_hari_lewat_jatuh_tempo: int = 0), izin "piutang":
     customer dengan sisa piutang terbesar, jumlah faktur, dan hari terlama lewat jatuh tempo.
   - margin_produk(jumlah: int = 5), izin "hpp":
     margin kotor per produk bulan terakhir (harga jual dibanding HPP per unit), dari yang paling tipis.

Selesai kalau `python -m pytest tests/test_tahap5a.py -q` lulus dan tahap sebelumnya tetap lulus.
```

## Cek hasil

Jalankan ulang ERP (`Ctrl+C` di terminal server, lalu `python -m server`). Di panel Asisten, sebagai `budi` lalu sebagai `andi`, kirim:

```
Buat ringkasan pagi untuk saya: stok yang di bawah minimum, piutang yang paling perlu ditagih, dan produk dengan margin paling tipis. Urutkan dari yang paling mendesak, maksimal 6 poin, sertakan angkanya.
```

Bandingkan: tool mana yang ditolak untuk Andi, dan bagaimana asisten menjelaskannya?

Bonus (butuh Node.js, lihat README bagian "Mengubah tampilan"): tombol **Briefing pagi** di halaman Ringkasan yang mengirim pertanyaan di atas lewat `ai.tanya(...)`.

## Siapkan untuk ditunjukkan (2 menit)

1. Kirim pertanyaannya di depan kelas, buka langkah agent.
2. Satu kalimat: fitur ini menggantikan pekerjaan apa di klien kalian?
3. Satu hal yang masih kurang sebelum fitur ini layak dirilis.
