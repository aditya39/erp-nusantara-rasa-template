#!/usr/bin/env bash
# Mengembalikan data ke kondisi awal (mis. setelah gladi): database dibuat ulang dari seed kit,
# indeks RAG diisi ulang, data tambahan ERP dimigrasi ulang. Model Ollama TIDAK dihapus.
set -euo pipefail
cd "$(dirname "$0")/.."
KIT=../kit/asisten-erp-ai

# Password DB dari .env folder ini ikut dipakai compose kit, supaya volume baru memakai password yang sama
# dengan URL koneksi ERP (lihat docker-compose.yml). DB_BIND/OLLAMA_BIND juga, supaya database server bersama
# tetap terbuka ke jaringan kelas setelah dibuat ulang. Variabel yang sudah ada di environment tidak ditimpa.
for v in DB_ADMIN_PASSWORD ERP_APP_PASSWORD DB_BIND OLLAMA_BIND; do
  if [ -z "${!v:-}" ] && [ -f .env ]; then
    nilai=$(sed -n "s/^${v}=//p" .env | tail -1 | tr -d "\"'\r")
    if [ -n "$nilai" ]; then export "$v=$nilai"; fi
  fi
done

VOL=$(docker inspect erp-ai-db --format '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}{{.Name}}{{end}}{{end}}' 2>/dev/null || true)
VOL=${VOL:-asisten-erp-ai_erp-data}    # container database belum ada (mis. setelah docker compose down): nama volume bawaan
echo "Menghapus database (volume $VOL)…"
(cd "$KIT" && docker compose rm -sf db >/dev/null)
if docker volume inspect "$VOL" >/dev/null 2>&1; then docker volume rm "$VOL" >/dev/null; fi
(cd "$KIT" && docker compose up -d db)
until docker inspect -f '{{.State.Health.Status}}' erp-ai-db 2>/dev/null | grep -q healthy; do sleep 2; done
sleep 2

if docker inspect erp-nusantara-rasa >/dev/null 2>&1; then
  echo "Mode Docker: buat ulang container ERP (migrasi + indeks RAG otomatis, .env terbaru)…"
  docker compose up -d --force-recreate --no-deps erp >/dev/null
  echo "Selesai. Pantau: docker compose logs -f erp"
else
  PY=$(pwd)/.venv/bin/python
  if [ -n "${DB_ADMIN_PASSWORD:-}" ]; then
    export DATABASE_URL_ADMIN="${DATABASE_URL_ADMIN:-postgresql://erp_admin:${DB_ADMIN_PASSWORD}@localhost:5433/erp}"
  fi
  echo "Mengisi ulang indeks dokumen (RAG)…"
  (cd "$KIT" && "$PY" -m asisten.rag ingest)
  echo "Migrasi ERP…"
  "$PY" -m server.migrasi
  echo "Selesai. Restart server ERP (Ctrl+C lalu scripts/jalankan.sh)."
fi
