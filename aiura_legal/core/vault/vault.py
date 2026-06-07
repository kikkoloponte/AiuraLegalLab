"""
PII Vault — cifratura AES-256-GCM per entity map PII.

Salva in MongoDB `pii_vault` la mappa entità → placeholder anonimizzato,
cifrata con AES-256-GCM. Permette di:
  - Recuperare il mapping per de-anonimizzare una risposta verso l'avvocato
  - Dimostrare che il sistema non ha trasmesso PII in chiaro al modello LLM
  - Garantire che PII di clienti diversi siano isolate per workspace

Schema documento `pii_vault`:
  {
    "_id":            ObjectId,
    "document_id":   str,
    "workspace":     str,
    "nonce_b64":     str,       # base64 del nonce GCM (12 byte)
    "ciphertext_b64": str,      # base64 di ciphertext+tag (16 byte tag)
    "created_at":    datetime,
    "updated_at":    datetime,
  }

Chiave AES-256:
  Letta da AIURA_PII_KEY (hex, 64 caratteri = 32 byte).
  In sviluppo, se non impostata: chiave temporanea generata in memoria (warning).
  In produzione: AIURA_PII_KEY obbligatoria.
"""
from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timezone
from typing import Optional

from loguru import logger

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "cryptography non installato. Esegui: pip install cryptography>=42.0"
    ) from exc


_KEY_ENV_VAR = "AIURA_PII_KEY"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PiiVault:
    """
    Cifratura/decifratura AES-256-GCM per entity map PII.
    Storage in MongoDB `pii_vault`.

    Utilizzo:
        vault = PiiVault.from_env(mongo_db)

        # Salva entity map cifrata
        await vault.store("doc123", "default", {"MARIO ROSSI": "[PER_1]"})

        # Recupera entity map in chiaro
        entity_map = await vault.retrieve("doc123")

        # Rimuovi
        await vault.delete("doc123")

    Cifratura diretta (senza MongoDB):
        nonce, ct = vault.encrypt('{"key": "value"}')
        plaintext = vault.decrypt(nonce, ct)
    """

    def __init__(self, mongo_db, key: bytes) -> None:
        if len(key) != 32:
            raise ValueError(
                f"Chiave AES-256 deve essere 32 byte, ricevuta {len(key)} byte"
            )
        self._db = mongo_db
        self._aesgcm = AESGCM(key)

    # ------------------------------------------------------------------
    # Factory methods
    # ------------------------------------------------------------------

    @classmethod
    def from_env(cls, mongo_db) -> "PiiVault":
        """
        Crea PiiVault leggendo la chiave da AIURA_PII_KEY (env var).
        Se non impostata, genera una chiave temporanea (solo per sviluppo).
        """
        key_hex = os.environ.get(_KEY_ENV_VAR, "").strip()
        if key_hex:
            try:
                key = bytes.fromhex(key_hex)
            except ValueError as exc:
                raise ValueError(
                    f"AIURA_PII_KEY non valida (deve essere hex 64 char): {exc}"
                ) from exc
            logger.debug("[PiiVault] Chiave caricata da AIURA_PII_KEY")
        else:
            # os.urandom è più portabile di AESGCM.generate_key su alcuni OS/provider
            key = os.urandom(32)
            logger.warning(
                "[PiiVault] AIURA_PII_KEY non impostata — "
                "chiave temporanea in memoria (solo sviluppo). "
                "Imposta AIURA_PII_KEY in produzione."
            )
        return cls(mongo_db, key)

    @classmethod
    def from_key(cls, mongo_db, key: bytes) -> "PiiVault":
        """Crea PiiVault con chiave esplicita (utile nei test)."""
        return cls(mongo_db, key)

    # ------------------------------------------------------------------
    # Primitivi crittografici
    # ------------------------------------------------------------------

    def encrypt(self, plaintext: str) -> tuple[bytes, bytes]:
        """
        Cifra plaintext con AES-256-GCM.

        Returns:
            (nonce, ciphertext_with_tag) — entrambi bytes.
            Il tag GCM (16 byte) è incluso in fondo a ciphertext.
        """
        nonce = os.urandom(12)   # 96-bit nonce — best practice per GCM
        ct = self._aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        return nonce, ct

    def decrypt(self, nonce: bytes, ciphertext: bytes) -> str:
        """
        Decifra e verifica autenticità con AES-256-GCM.

        Raises:
            cryptography.exceptions.InvalidTag se ciphertext è manomesso.
        """
        plaintext = self._aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode("utf-8")

    # ------------------------------------------------------------------
    # Storage MongoDB
    # ------------------------------------------------------------------

    async def store(
        self,
        document_id: str,
        workspace: str,
        entity_map: dict,
    ) -> None:
        """
        Cifra l'entity map e la salva in `pii_vault`.
        Upsert: sovrascrive se esiste già un record per document_id.

        Args:
            document_id: _id del documento in `documents`
            workspace:   workspace del documento
            entity_map:  dict {entità_originale: placeholder_anonimizzato}
        """
        plaintext = json.dumps(entity_map, ensure_ascii=False, sort_keys=True)
        nonce, ct = self.encrypt(plaintext)
        now = _utcnow()

        await self._db["pii_vault"].update_one(
            {"document_id": document_id},
            {
                "$set": {
                    "document_id": document_id,
                    "workspace": workspace,
                    "nonce_b64": base64.b64encode(nonce).decode("ascii"),
                    "ciphertext_b64": base64.b64encode(ct).decode("ascii"),
                    "updated_at": now,
                },
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
        )
        logger.debug(
            f"[PiiVault] Entity map salvata: doc={document_id}, "
            f"entries={len(entity_map)}"
        )

    async def retrieve(self, document_id: str) -> Optional[dict]:
        """
        Recupera e decifra l'entity map per document_id.

        Returns:
            dict entity map, oppure None se il record non esiste.

        Raises:
            cryptography.exceptions.InvalidTag se il ciphertext è corrotto.
        """
        record = await self._db["pii_vault"].find_one({"document_id": document_id})
        if record is None:
            return None

        nonce = base64.b64decode(record["nonce_b64"])
        ct    = base64.b64decode(record["ciphertext_b64"])
        plaintext = self.decrypt(nonce, ct)
        return json.loads(plaintext)

    async def delete(self, document_id: str) -> bool:
        """
        Rimuove il record vault per document_id.

        Returns:
            True se il record è stato rimosso, False se non esisteva.
        """
        result = await self._db["pii_vault"].delete_one({"document_id": document_id})
        deleted = result.deleted_count > 0
        if deleted:
            logger.debug(f"[PiiVault] Record rimosso: doc={document_id}")
        return deleted

    async def exists(self, document_id: str) -> bool:
        """Verifica l'esistenza di un record vault per document_id."""
        count = await self._db["pii_vault"].count_documents(
            {"document_id": document_id}, limit=1
        )
        return count > 0
