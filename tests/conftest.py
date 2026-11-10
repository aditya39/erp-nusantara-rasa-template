"""
Tes penerimaan per tahap. JANGAN diubah: tes ini adalah definisi "selesai" untuk setiap tahap.

  python -m pytest tests/test_tahap1.py -q     # satu tahap
  python scripts/cek_tahap.py                  # papan status semua tahap

Model sungguhan tidak dipanggil di sini. Agent diuji dengan model palsu (ModelPalsu) yang
jawabannya sudah ditentukan, supaya tes cepat dan hasilnya selalu sama. Database dipakai
sungguhan (role read-only), jadi angka di tes berasal dari data ERP.
"""
import json
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import psycopg
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from asisten import config, llm  # noqa: E402


@pytest.fixture(scope="session")
def butuh_db():
    try:
        psycopg.connect(config.DATABASE_URL, connect_timeout=5).close()
    except psycopg.OperationalError as e:
        pytest.skip(f"Database tidak dapat dihubungi, cek DATABASE_URL di .env ({str(e).splitlines()[0]})")


@pytest.fixture(autouse=True)
def _log_audit_terpisah(tmp_path, monkeypatch):
    """Selama tes, jejak audit ditulis ke folder sementara supaya Log aktivitas AI tidak penuh catatan uji."""
    try:
        from asisten import audit
    except ImportError:   # asisten/audit.py baru ada di Tahap 3
        return
    monkeypatch.setattr(audit, "FILE_LOG", tmp_path / "aktivitas-uji.jsonl", raising=False)


class ModelPalsu:
    """
    Pengganti model. `langkah` berisi balasan berurutan:
      ("nama_tool", {argumen})  -> model meminta tool
      "teks"                    -> model memberi jawaban akhir
    Bila langkah habis, balasan terakhir diulang (untuk menguji batas langkah).
    Semua pesan yang dikirim agent ke model tersimpan di .dikirim.
    """

    def __init__(self, langkah):
        self.langkah = list(langkah)
        self.dikirim: list[dict] = []
        self.chat = NS(completions=NS(create=self.create))

    def create(self, **kw):
        self.dikirim.append(kw)
        isi = self.langkah.pop(0) if len(self.langkah) > 1 else self.langkah[0]
        if isinstance(isi, tuple):
            nama, argumen = isi
            tc = NS(id=f"panggilan_{len(self.dikirim)}", type="function",
                    function=NS(name=nama, arguments=json.dumps(argumen)))
            msg = NS(content="", tool_calls=[tc])
        else:
            msg = NS(content=isi, tool_calls=None)
        return NS(choices=[NS(message=msg)], usage=NS(prompt_tokens=10, completion_tokens=5))

    def pesan_tool(self) -> list[str]:
        """Isi semua pesan role "tool" yang pernah dikirim agent ke model (hasil tool)."""
        hasil = []
        for kw in self.dikirim:
            for m in kw.get("messages", []):
                if isinstance(m, dict) and m.get("role") == "tool" and m.get("content") not in hasil:
                    hasil.append(m.get("content"))
        return hasil


@pytest.fixture
def model_palsu(monkeypatch):
    """Pasang ModelPalsu sebagai pengganti klien model. Pakai: model = model_palsu([...langkah...])."""
    def pasang(langkah):
        m = ModelPalsu(langkah)
        monkeypatch.setattr(llm, "buat_klien", lambda cfg: m)
        return m
    return pasang


def tanya(pertanyaan="pertanyaan uji", pengguna="budi"):
    """Jalankan agent sampai selesai dan kembalikan semua event."""
    from asisten import agent
    return list(agent.jalankan(pertanyaan, pengguna))


def teks_json(hasil) -> str:
    return json.dumps(hasil, ensure_ascii=False, default=str)
