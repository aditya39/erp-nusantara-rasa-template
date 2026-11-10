# Tahap 5B — Draft surat penagihan

**Waktu:** 22 menit. **Butuh Tahap 4.** **Hasil:** asisten menyusun draft surat penagihan dari data faktur dan mengutip kebijakan penagihan.

**Untuk siapa di klien:** staf finance yang menyalin nomor faktur ke template surat satu per satu.
**Pola:** tool (data piutang) + RAG (kebijakan) dalam satu jawaban. Hasilnya draft: manusia yang membaca dan mengirim.

## Prompt untuk Claude Code

```
Kerjakan Tahap 5B (kartu/5b-surat-penagihan.md). Ikuti AGENTS.md.

1. Tambahkan tool piutang_customer(customer: str) di asisten/tools_tambahan.py, izin "piutang":
   rincian faktur belum lunas milik SATU customer (nomor_faktur, tanggal, jatuh_tempo, sisa,
   hari_lewat_jatuh_tempo), total sisa, dan hari terlama lewat jatuh tempo.
   Nama customer dicocokkan dengan toleran (pakai _cocokkan dari tools.py); kalau tidak ketemu
   atau ambigu, kembalikan error + kandidat.

Selesai kalau `python -m pytest tests/test_tahap5b.py -q` lulus dan tahap sebelumnya tetap lulus.
```

## Cek hasil

Jalankan ulang ERP (`Ctrl+C` di terminal server, lalu `python -m server`). Login sebagai `sari`, buka **Keuangan › Piutang usaha** (CV Laju Makmur Abadi ada di urutan atas), lalu kirim di panel Asisten:

```
Buatkan draft surat penagihan untuk CV Laju Makmur Abadi. Cantumkan nomor faktur, sisa tagihan, dan jumlah hari lewat jatuh tempo. Jelaskan langkah berikutnya sesuai kebijakan penagihan perusahaan dan sebutkan nomor dokumen kebijakannya.
```

Bonus (butuh Node.js): tombol **Draft surat penagihan** di baris customer pada halaman Piutang usaha.

Periksa suratnya:

1. Nomor faktur dan angkanya sama dengan hasil tool?
2. Tahap penagihan yang disebut sesuai dengan jumlah hari lewat jatuh tempo? Cocokkan dengan dokumen Kebijakan Kredit dan Penagihan di menu **SOP & Kebijakan**.
3. Nomor dokumen kebijakannya disebut?

## Siapkan untuk ditunjukkan (2 menit)

1. Klik tombolnya di depan kelas, buka langkah agent.
2. Satu kalimat: berapa lama pekerjaan ini kalau dikerjakan manual di klien kalian?
3. Satu hal yang masih kurang sebelum fitur ini layak dirilis.
