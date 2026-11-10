# ERP Nusantara Rasa — template praktik "AI di aplikasi ERP"

Aplikasi ERP lengkap untuk praktik Hari 2 workshop Agentic AI: penjualan, sales order, keuangan, persediaan,
produksi & HPP, dokumen, pengguna & hak akses, log aktivitas. Panel **Asisten** dan tombol "Tanya Asisten"
sudah ada di layar, tetapi **AI-nya belum dipasang**. Kalian yang membangun otaknya, tahap demi tahap, dengan
Claude Code.

> PT Nusantara Rasa adalah perusahaan **fiktif**. Seluruh data adalah data dummy (Mei 2025 – Oktober 2026, posisi
> 31-10-2026). Jangan memakai source code atau data kantor di proyek ini.

```
Browser (Angular 21 + PrimeNG, sudah di-build)
   │  REST + SSE
   ▼
FastAPI (server/)  ── role erp_app (transaksi ERP)
   │
   └── /api/ai/chat (server/routers/ai.py, sudah jadi)
          └── paket asisten/  ◄── INI YANG KALIAN BANGUN: tools, agent loop, pengaman, RAG, fitur
                 ├── role erp_ai_readonly (hanya membaca view schema "ai")
                 ├── model chat: Claude Haiku lewat API key dari mentor
                 └── embedding: Ollama bge-m3 di laptop sendiri
PostgreSQL 17 + pgvector (docker compose)
```

## Mengenal ERP ini

| Menu | Halaman | Aturan yang ditegakkan kode ERP (bukan AI) |
|---|---|---|
| Ringkasan | KPI, omzet 12 bulan, kartu "Perlu tindakan" (dengan tombol Tanya Asisten), umur piutang, aktivitas | isi mengikuti hak akses user |
| Penjualan | Sales order (daftar, buat, detail + persetujuan), Faktur penjualan, Customer, Laporan penjualan | diskon standar per segmen (Distributor 12%, Retail Modern 6%, Toko 2%); diskon tambahan maks 1,5% untuk Sales Supervisor, maks 3% dengan persetujuan Manajer Penjualan; tanpa diskon tambahan bila tunggakan > 30 hari; SO melebihi limit kredit → Ditahan (Finance); tunggakan > 60 hari → credit hold (Direktur); stok gudang dicek |
| Keuangan | Piutang usaha (umur piutang + tahap penagihan), Penerimaan pembayaran | pembayaran dialokasikan ke faktur tertua lebih dulu |
| Persediaan | Stok gudang, Mutasi stok | faktur mengurangi stok dan mencatat mutasi |
| Produksi | Produk (HPP, margin, resep), Bahan baku (riwayat harga), Analisis HPP | HPP naik > 8% → tanda wajib kajian |
| SOP & Kebijakan | 6 dokumen SOP dan kebijakan (sumber RAG di Tahap 4) | – |
| Pengaturan | Pengguna & hak akses, Log aktivitas (termasuk setiap pertanyaan ke Asisten) | perubahan izin tercatat |

Aturan bisnis ada di `server/logika.py` dan dokumen di `dokumen/`. Prinsipnya: **aturan ditegakkan kode ERP; AI hanya
membaca data, menjelaskan aturan dari dokumen, dan menyiapkan draft.**

## Yang perlu dipasang sebelum hari H

Kerjakan di rumah atau kantor, karena ada unduhan sekitar 2 GB. Di ruang workshop unduhan bersamaan akan lambat.

| Yang dipasang | Cara | Cek |
|---|---|---|
| Git | sudah ada di macOS; Windows: https://git-scm.com | `git --version` |
| Python 3.10 atau lebih baru | https://www.python.org/downloads | `python3 --version` (Windows: `py --version`) |
| Docker Desktop | https://www.docker.com/products/docker-desktop | `docker --version`, dan aplikasinya sedang jalan |
| Ollama | https://ollama.com/download (macOS: `brew install --cask ollama`) | `ollama --version` |
| Claude Code, sudah login | sama seperti Hari 1 | `claude` membuka sesi tanpa diminta login |

Lalu unduh semua yang besar sekali saja:

```bash
git clone https://github.com/aditya39/erp-nusantara-rasa-template.git
cd erp-nusantara-rasa-template
docker compose up -d          # unduh image database (±450 MB) dan isi data dummy
ollama pull bge-m3            # model embedding untuk RAG (±1,2 GB)
```

`docker compose ps` harus menunjukkan `healthy`, dan `ollama list` harus memuat `bge-m3`. Model chat `qwen3:8b`
tidak perlu diunduh; di workshop model chat memakai Claude Haiku lewat API.

## Menjalankan

```bash
python3 -m venv .venv                 # Windows: py -m venv .venv
source .venv/bin/activate             # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                  # Windows: copy .env.example .env
```

Buka `.env`, lalu:

1. Di blok **PROFIL (d)** paling bawah, hapus tanda `#` di kelima barisnya dan isi `LOKAL_API_KEY` dengan API key dari mentor.
2. Isi `RAG_KOLEKSI` dengan nama kamu, huruf kecil, misalnya `budi`.

Lalu:

```bash
docker compose up -d                  # kalau database belum jalan
python scripts/cek_setup.py           # semua baris ✓
python -m server                      # buka http://localhost:8080
```

Login dengan salah satu akun di bawah (password semua `demo123`). Klik **Asisten** di kanan atas untuk membuka panel.

| User | Jabatan | Hak akses data (dipakai juga oleh asisten) |
|---|---|---|
| `budi` | Direktur Operasional | semua data, termasuk Pengaturan |
| `andi` | Sales Supervisor | produk, penjualan, stok, dokumen, buat SO (**tanpa HPP dan piutang**) |
| `sari` | Staf Finance & Accounting | produk, penjualan, HPP, piutang, dokumen (**tidak boleh buat SO**) |
| `dewi` | Manajer Penjualan | produk, penjualan, piutang, stok, dokumen, buat SO |
| `agus` | Supervisor Gudang | produk, stok, dokumen |
| `rudi` | Administrator Sistem | dokumen, Pengaturan |

## Tahap

Buka Claude Code di folder ini (`claude`), lalu ikuti kartu secara berurutan. Setiap kartu berisi prompt yang bisa
disalin, cara mengecek hasil, dan hal yang perlu kalian pahami dari kode yang ditulis Claude Code.

| Tahap | Kartu | Yang terlihat di ERP setelah selesai |
|---|---|---|
| 0 | `kartu/0-kenali-template.md` | ERP berjalan. Asisten menjawab tanpa data |
| 1 | `kartu/1-tool-penjualan.md` | Model meminta tool yang benar, tetapi belum ada yang menjalankannya |
| 2 | `kartu/2-agent-loop.md` | Asisten menjawab dari data. Tombol **Telusuri penyebab** di Analisis HPP bekerja |
| 3 | `kartu/3-pengaman.md` | User tanpa izin ditolak oleh kode. Setiap pertanyaan tercatat |
| 4 | `kartu/4-rag.md` | Asisten menjawab aturan dari dokumen SOP dan menyebut sumbernya |
| 5 | `kartu/5a-briefing-pagi.md`, `5b-surat-penagihan.md`, `5c-email-jadi-draft-so.md` | Satu fitur pilihan: briefing pagi, draft surat penagihan, atau email pesanan menjadi draft sales order |

Papan status: `python scripts/cek_tahap.py`. Kode Python berubah? Jalankan ulang server (`Ctrl+C`, lalu `python -m server`).

## Kalau macet

- Baca pesan tes yang gagal: `python scripts/cek_tahap.py 2`. Pesannya menjelaskan apa yang diharapkan. Tempel ke Claude Code.
- Waktu habis: pasang kunci tahap itu supaya bisa lanjut, `python scripts/pasang_kunci.py 2`. File kalian disalin dulu ke `cadangan/`.
- Database tidak bisa dihubungi: Docker Desktop sudah jalan? `docker compose ps` harus `healthy`. Lihat log: `docker compose logs db`.
- Port 5433 sudah dipakai program lain: `DB_PORT=5434 docker compose up -d`, lalu di `.env` ganti `5433` menjadi `5434` di
  `DATABASE_URL` dan `DATABASE_URL_ADMIN`, dan tambahkan dua baris `ERP_DATABASE_URL=postgresql://erp_app:aplikasi_erp@localhost:5434/erp`
  serta `ERP_DATABASE_URL_ADMIN=postgresql://erp_admin:admin_workshop@localhost:5434/erp`.
- Port 8080 sudah dipakai: tambahkan `ERP_PORT=8081` dan ubah `ERP_URL=http://localhost:8081` di `.env`.
- Embedding gagal (Tahap 4): aplikasi Ollama sudah jalan? `ollama list` harus memuat `bge-m3`.
- Model chat gagal: cek blok PROFIL (d) dan koneksi internet. Pesan 401 berarti key salah; 429 berarti batas pemakaian tercapai, tunggu sebentar.
- Data ingin kembali ke awal: `docker compose down -v`, lalu `docker compose up -d`.

### Kalau Docker tidak bisa dipasang

Database bisa juga dipasang langsung (PostgreSQL 17 + ekstensi pgvector), lalu diisi dengan file `db/init/*.sql` secara
berurutan. Minta bantuan Claude Code dengan prompt seperti ini (belum diuji di semua sistem operasi):

```
Tolong pasang PostgreSQL 17 dengan ekstensi pgvector di laptop ini tanpa Docker, port 5433.
Buat database "erp" dengan superuser erp_admin password admin_workshop, lalu jalankan
file db/init/01_schema.sql sampai 04_latihan.sql berurutan sebagai erp_admin.
Jangan mengubah file di folder db/. Jelaskan setiap perintah sebelum menjalankannya.
Setelah selesai, jalankan python scripts/cek_setup.py.
```

## Mengubah tampilan (bonus, tidak wajib)

Tidak ada tahap yang mewajibkan perubahan frontend. Kalau ingin menambah tombol AI sendiri di halaman Angular
(misalnya tombol **Briefing pagi** di Ringkasan), butuh Node.js 20+:

```bash
cd frontend
npm ci                     # sekali, ±300 MB
npm start                  # dev server http://localhost:4200, hot reload, /api diteruskan ke :8080
npx ng build               # setelah selesai: memperbarui frontend/dist yang dipakai python -m server
```

Tombol AI cukup memanggil `ai.tanya("pertanyaan")` dari service `Asisten` (`frontend/src/app/ai/asisten.ts`). Contohnya
ada di `frontend/src/app/pages/produksi/hpp.ts` (tombol "Telusuri penyebab").

## Catatan keamanan

- Asisten memakai role database `erp_ai_readonly`: hanya SELECT pada view schema `ai` dan koleksi dokumen. Aplikasi
  ERP memakai role `erp_app`. Password default di repo ini hanya untuk database di laptop sendiri (`127.0.0.1`);
  jangan membuka port database ke jaringan.
- Hak akses user di ERP disalin ke asisten oleh `server/routers/ai.py`. Mencabut izin di **Pengaturan › Pengguna & hak
  akses** langsung membuat tool AI terkait ditolak, oleh kode, bukan oleh prompt.
- `.env` tidak ikut git. Jangan menempel isinya ke Slack atau ke prompt. `.claude/settings.json` melarang Claude Code
  membaca `.env` dan `kunci.zip`, serta mengubah `tests/`.
- Dengan Claude Haiku lewat API, pertanyaan dan hasil query dikirim ke penyedia model. Di sini semuanya data dummy.
- Model tidak pernah diberi tool yang menyimpan. Sales order disimpan oleh endpoint ERP setelah user menekan **Simpan**.

## Struktur

| Folder | Isi |
|---|---|
| `asisten/` | otak asisten: yang dibangun peserta (lihat `AGENTS.md`) |
| `server/` | backend ERP (FastAPI), sudah jadi |
| `frontend/` | Angular; hasil build ada di `frontend/dist/` |
| `db/init/` | schema, data dummy, view `ai`, role (dipakai `docker compose`) |
| `dokumen/` | SOP dan kebijakan (menu SOP & Kebijakan, sumber RAG) |
| `dokumen-uji/` | email PO dan dokumen uji untuk Tahap 4 dan fitur C |
| `kartu/`, `tests/`, `scripts/` | kartu tahap, tes penerimaan, papan status, pemasang kunci |
