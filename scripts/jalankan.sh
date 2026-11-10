#!/usr/bin/env bash
# Menjalankan ERP Nusantara Rasa: cek database & model, build frontend bila belum, lalu start server.
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

if ! docker inspect -f '{{.State.Health.Status}}' erp-ai-db 2>/dev/null | grep -q healthy; then
  echo "Database belum jalan. Menjalankan: (cd $KIT && docker compose up -d)"
  (cd "$KIT" && docker compose up -d)
  until docker inspect -f '{{.State.Health.Status}}' erp-ai-db 2>/dev/null | grep -q healthy; do sleep 2; done
fi

curl -sf http://localhost:11434/api/tags >/dev/null || echo "PERINGATAN: Ollama tidak terdeteksi di localhost:11434 (Asisten AI lokal tidak akan menjawab)."

if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi

if [ ! -f frontend/dist/frontend/browser/index.html ]; then
  echo "Build frontend (sekali saja)…"
  (cd frontend && npm install --no-audit --no-fund && npm run build)
fi

exec .venv/bin/python -m server "$@"
