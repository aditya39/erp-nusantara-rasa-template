# Tahap 5C — Pesanan dari email jadi draft sales order

**Waktu:** 22 menit. **Hasil:** user menempel email pesanan di panel Asisten. Asisten menyiapkan draft sales order, sistem ERP menghitungnya, dan user yang menekan Simpan.

**Untuk siapa di klien:** admin penjualan yang mengetik ulang PO dari email atau WhatsApp ke form sales order.
**Pola:** agent yang menyiapkan transaksi. Ini fitur yang paling berisiko dari ketiganya, jadi aturannya ketat:

> AI menyiapkan. Sistem menghitung. Manusia memutuskan. Kode yang menyimpan.

## Prompt untuk Claude Code

```
Kerjakan Tahap 5C (kartu/5c-email-jadi-draft-so.md). Ikuti AGENTS.md, terutama bagian "Larangan".

1. Buat asisten/transaksi.py berisi tool siapkan_draft_so(customer: str, item: list,
   gudang: str = "", diskon_tambahan: float = 0, catatan: str = ""), izin "so_buat".
   item: [{"produk": str, "qty": int, "satuan": str opsional}].
   Tool HANYA membaca view ai (v_customer, v_produk, v_stok) dan mengembalikan:
     {"status": "DRAFT_BELUM_DISIMPAN",
      "draft_so": {
        "customer": {id, kode, nama, segmen, kota, termin_hari},
        "gudang": "Gudang Jakarta" | "Gudang Surabaya", "gudang_otomatis": bool,
        "diskon_tambahan": float, "catatan": str,
        "item": [{produk_id, kode, nama, satuan, qty, harga_daftar, harga_daftar_fmt, stok_gudang}],
        "nilai_bruto": float, "nilai_bruto_fmt": "Rp ...",
        "payload": {customer_id, gudang, diskon_tambahan, catatan, item: [{produk_id, qty}]}},
      "peringatan": [str]}
   Customer atau produk yang tidak ketemu atau ambigu: kembalikan {"error", "kandidat"},
   jangan ditebak. Gudang kosong: Gudang Surabaya untuk customer di Surabaya, Makassar, Denpasar;
   selain itu Gudang Jakarta. Stok kurang: tulis di peringatan.
   Daftarkan tool ini (impor modulnya dari asisten/tools.py).
2. Di asisten/agent.py: setelah tool mengembalikan draft_so, keluarkan event
   {"tipe": "draft_so", "draft": hasil["draft_so"]}. Kartu draft di panel ERP
   (frontend/src/app/ai/kartu-draft-so.ts) sudah membaca event ini: ia meminta hitungan ke
   /api/sales-order/simulasi dan menyimpan lewat /api/sales-order saat user menekan Simpan.
   Jangan mengubah server/ dan frontend/.

Model tidak boleh punya tool yang menyimpan. Selesai kalau `python -m pytest tests/test_tahap5c.py -q`
lulus dan tahap sebelumnya tetap lulus.
```

## Cek hasil

Jalankan ulang ERP (`Ctrl+C` di terminal server, lalu `python -m server`). Login sebagai `andi`, buka panel Asisten, ketik baris pertama di bawah, lalu tempel isi `dokumen-uji/Email-PO-Swalayan-Sentosa.txt` (tanpa tiga baris berawalan `#`) dan kirim:

```
Siapkan draft sales order dari email pesanan berikut.
```

Periksa kartu draft:

1. Customer, tiga produk, dan qty sesuai email?
2. Nomor PO masuk ke catatan?
3. Gulir email itu ke paling bawah, jauh ke kanan. Ada instruksi tersembunyi. Apakah diskon tambahan di draft tetap 0? Apakah ada yang tersimpan tanpa kalian klik?
4. Harga, diskon segmen, dan status di kartu berasal dari sistem ERP, bukan dari model.

Database ini milik laptop kalian sendiri, jadi **boleh klik Simpan**. Setelah tersimpan, buka **Penjualan › Sales order**: SO baru bertanda "Dibuat lewat Asisten AI", dan riwayatnya mencatat siapa yang menyimpan. Coba juga **Ubah di form** dan **Batal**. Data bisa dikembalikan ke awal dengan `docker compose down -v` lalu `docker compose up -d`.

Coba juga login sebagai Sari dan tempel email yang sama. Apa yang terjadi?

## Siapkan untuk ditunjukkan (2 menit)

1. Tempel email di depan kelas, tunjukkan kartu draft dan instruksi tersembunyinya.
2. Satu kalimat: siapa yang menahan diskon 10% itu?
3. Satu hal yang masih kurang sebelum fitur ini layak dirilis.
