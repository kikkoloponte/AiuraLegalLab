"""
test_pii_vault.py — test per PiiVault (AES-256-GCM, MongoDB).

Copertura:
  TestEncryptDecrypt   (5) — round-trip, nonce unico, testo vuoto, unicode, tag manomesso
  TestFromEnv          (3) — chiave da env var, chiave temporanea se assente, chiave hex errata
  TestFromKey          (2) — chiave 32 byte ok, lunghezza errata
  TestStore            (4) — upsert, sovrascrittura, chiave non in chiaro nel DB
  TestRetrieve         (3) — happy path, not found, dict complesso
  TestDelete           (2) — elimina, non esisteva
  TestExists           (2) — esiste, non esiste
"""
from __future__ import annotations

import os
from unittest.mock import patch

import pytest
import mongomock_motor

from aiura_legal.core.vault.vault import PiiVault
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_db():
    client = mongomock_motor.AsyncMongoMockClient()
    return client["aiura_legal"]


@pytest.fixture
def test_key() -> bytes:
    """Chiave AES-256 deterministica per i test."""
    return bytes(range(32))   # 32 byte 0x00..0x1F


@pytest.fixture
def vault(mock_db, test_key) -> PiiVault:
    return PiiVault.from_key(mock_db, test_key)


# ---------------------------------------------------------------------------
# TestEncryptDecrypt
# ---------------------------------------------------------------------------

class TestEncryptDecrypt:
    def test_roundtrip(self, vault):
        plaintext = '{"MARIO ROSSI": "[PER_1]", "CF": "[CF_1]"}'
        nonce, ct = vault.encrypt(plaintext)
        result = vault.decrypt(nonce, ct)
        assert result == plaintext

    def test_nonce_is_unique_each_call(self, vault):
        nonces = [vault.encrypt("test")[0] for _ in range(5)]
        # Tutti i nonce devono essere diversi
        assert len(set(nonces)) == 5

    def test_empty_string_roundtrip(self, vault):
        nonce, ct = vault.encrypt("{}")
        assert vault.decrypt(nonce, ct) == "{}"

    def test_unicode_roundtrip(self, vault):
        text = '{"Ångström Società": "[ORG_1]", "Renée Dupré": "[PER_1]"}'
        nonce, ct = vault.encrypt(text)
        assert vault.decrypt(nonce, ct) == text

    def test_tampered_ciphertext_raises(self, vault):
        nonce, ct = vault.encrypt("sensitive")
        tampered = bytes([ct[0] ^ 0xFF]) + ct[1:]
        with pytest.raises(InvalidTag):
            vault.decrypt(nonce, tampered)


# ---------------------------------------------------------------------------
# TestFromEnv
# ---------------------------------------------------------------------------

class TestFromEnv:
    def test_key_loaded_from_env(self, mock_db):
        key_bytes = bytes(range(32))
        key_hex = key_bytes.hex()
        with patch.dict(os.environ, {"AIURA_PII_KEY": key_hex}):
            v = PiiVault.from_env(mock_db)
        # Verifica round-trip con la stessa chiave
        nonce, ct = v.encrypt("test")
        assert v.decrypt(nonce, ct) == "test"

    def test_temp_key_generated_if_env_absent(self, mock_db):
        with patch.dict(os.environ, {}, clear=True):
            if "AIURA_PII_KEY" in os.environ:
                del os.environ["AIURA_PII_KEY"]
            v = PiiVault.from_env(mock_db)
        # Deve funzionare ugualmente
        nonce, ct = v.encrypt("dev")
        assert v.decrypt(nonce, ct) == "dev"

    def test_invalid_hex_raises(self, mock_db):
        with patch.dict(os.environ, {"AIURA_PII_KEY": "not_hex_!@#"}):
            with pytest.raises(ValueError, match="AIURA_PII_KEY non valida"):
                PiiVault.from_env(mock_db)


# ---------------------------------------------------------------------------
# TestFromKey
# ---------------------------------------------------------------------------

class TestFromKey:
    def test_valid_32_byte_key(self, mock_db):
        key = os.urandom(32)
        v = PiiVault.from_key(mock_db, key)
        assert v is not None

    def test_wrong_key_length_raises(self, mock_db):
        with pytest.raises(ValueError, match="32 byte"):
            PiiVault.from_key(mock_db, b"short_key")


# ---------------------------------------------------------------------------
# TestStore
# ---------------------------------------------------------------------------

class TestStore:
    @pytest.mark.asyncio
    async def test_store_creates_record(self, vault, mock_db):
        entity_map = {"MARIO ROSSI": "[PER_1]"}
        await vault.store("doc1", "default", entity_map)
        record = await mock_db["pii_vault"].find_one({"document_id": "doc1"})
        assert record is not None
        assert record["workspace"] == "default"

    @pytest.mark.asyncio
    async def test_store_does_not_save_plaintext(self, vault, mock_db):
        await vault.store("doc2", "default", {"CF123456": "[CF_1]"})
        record = await mock_db["pii_vault"].find_one({"document_id": "doc2"})
        # La chiave PII non deve comparire in chiaro nel documento MongoDB
        record_str = str(record)
        assert "CF123456" not in record_str

    @pytest.mark.asyncio
    async def test_store_overwrites_existing(self, vault, mock_db):
        await vault.store("doc3", "default", {"OLD_KEY": "[PER_1]"})
        await vault.store("doc3", "default", {"NEW_KEY": "[PER_2]"})
        result = await vault.retrieve("doc3")
        assert "NEW_KEY" in result
        assert "OLD_KEY" not in result

    @pytest.mark.asyncio
    async def test_store_has_created_at(self, vault, mock_db):
        await vault.store("doc4", "ws1", {"k": "v"})
        record = await mock_db["pii_vault"].find_one({"document_id": "doc4"})
        assert "created_at" in record


# ---------------------------------------------------------------------------
# TestRetrieve
# ---------------------------------------------------------------------------

class TestRetrieve:
    @pytest.mark.asyncio
    async def test_retrieve_roundtrip(self, vault):
        entity_map = {"MARIO ROSSI": "[PER_1]", "CF ROSMAR80A01H501Z": "[CF_1]"}
        await vault.store("doc5", "default", entity_map)
        result = await vault.retrieve("doc5")
        assert result == entity_map

    @pytest.mark.asyncio
    async def test_retrieve_not_found_returns_none(self, vault):
        result = await vault.retrieve("nonexistent_doc")
        assert result is None

    @pytest.mark.asyncio
    async def test_retrieve_complex_dict(self, vault):
        entity_map = {
            "Mario Rossi": "[PER_1]",
            "Via Roma 1, Milano": "[LOC_1]",
            "RSSMRA80A01H501Z": "[CF_1]",
            "IT60X0542811101000000123456": "[IBAN_1]",
        }
        await vault.store("doc6", "default", entity_map)
        result = await vault.retrieve("doc6")
        assert result == entity_map


# ---------------------------------------------------------------------------
# TestDelete
# ---------------------------------------------------------------------------

class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_existing_returns_true(self, vault):
        await vault.store("doc7", "default", {"k": "v"})
        deleted = await vault.delete("doc7")
        assert deleted is True

    @pytest.mark.asyncio
    async def test_delete_nonexistent_returns_false(self, vault):
        deleted = await vault.delete("phantom_doc")
        assert deleted is False


# ---------------------------------------------------------------------------
# TestExists
# ---------------------------------------------------------------------------

class TestExists:
    @pytest.mark.asyncio
    async def test_exists_true_after_store(self, vault):
        await vault.store("doc8", "default", {"k": "v"})
        assert await vault.exists("doc8") is True

    @pytest.mark.asyncio
    async def test_exists_false_before_store(self, vault):
        assert await vault.exists("nope") is False
