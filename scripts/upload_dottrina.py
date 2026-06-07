"""
Carica tutti i PDF già scaricati in download/dottrina/ nell'API come corpus=dottrina.
Da usare dopo sync_dottrina.py --no-upload.

Uso:
  python scripts/upload_dottrina.py
  python scripts/upload_dottrina.py --workspace mio-studio
"""
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

import httpx
from loguru import logger

API_URL      = "http://127.0.0.1:8765"
DOWNLOAD_DIR = Path("download/dottrina")


async def main(workspace: str) -> None:
    # Verifica API
    try:
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{API_URL}/health", timeout=5)
            r.raise_for_status()
            logger.info(f"API online: {r.json().get('status')}")
    except Exception as exc:
        logger.error(f"API non raggiungibile: {exc}")
        return

    pdfs = sorted(DOWNLOAD_DIR.glob("*.pdf"))
    logger.info(f"PDF trovati in {DOWNLOAD_DIR}: {len(pdfs)}")

    ok = fail = 0
    async with httpx.AsyncClient(timeout=120) as client:
        for pdf_path in pdfs:
            logger.info(f"Upload: {pdf_path.name}")
            try:
                with open(pdf_path, "rb") as f:
                    resp = await client.post(
                        f"{API_URL}/ingest",
                        data={"workspace": workspace, "corpus": "dottrina"},
                        files={"file": (pdf_path.name, f, "application/pdf")},
                    )
                if resp.status_code in (200, 201):
                    data = resp.json()
                    logger.success(f"  ✅ doc_id={data.get('document_id')} chunks={data.get('chunk_count','?')}")
                    ok += 1
                else:
                    logger.error(f"  ❌ {resp.status_code}: {resp.text[:150]}")
                    fail += 1
            except Exception as exc:
                logger.error(f"  ❌ {exc}")
                fail += 1

    logger.info(f"\nCompletato: {ok} OK, {fail} errori")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--workspace", default="mio-studio")
    args = p.parse_args()
    asyncio.run(main(args.workspace))
