"""
Menjalankan ERP Nusantara Rasa.

  python -m server                  # http://localhost:8080
  python -m server --host 0.0.0.0   # bisa dibuka dari laptop lain di jaringan yang sama

"""
import argparse
import time

import psycopg
import uvicorn

from . import config, migrasi



ap = argparse.ArgumentParser()
ap.add_argument("--host", default=config.HOST)
ap.add_argument("--port", type=int, default=config.PORT)
ap.add_argument("--reload", action="store_true", help="muat ulang otomatis saat kode berubah (pengembangan)")
args = ap.parse_args()

for percobaan in range(30):                   # database mungkin belum siap (mis. baru dibuat di Docker)
    try:
        migrasi.jalankan()
        break
    except psycopg.OperationalError as e:
        print(f"Menunggu database… ({str(e).splitlines()[0][:90]})")
        time.sleep(2)
else:
    raise SystemExit("Database tidak dapat dihubungi.")


print(f"ERP Nusantara Rasa: http://{'localhost' if args.host in ('127.0.0.1', '0.0.0.0') else args.host}:{args.port}", flush=True)
uvicorn.run("server.app:app", host=args.host, port=args.port, reload=args.reload, log_level="warning")
