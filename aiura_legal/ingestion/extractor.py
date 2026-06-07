"""
Document Extractor — PDF / DOCX / TXT.
Normalizza il testo: rimuove hyphenation, comprime whitespace, preserva paragrafi.
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Tuple
from loguru import logger

# Import a livello modulo per permettere il mock nei test
try:
    from pdfminer.high_level import extract_text as pdf_extract
except ImportError:  # pragma: no cover
    pdf_extract = None  # type: ignore

try:
    from docx import Document as DocxDocument
except ImportError:  # pragma: no cover
    DocxDocument = None  # type: ignore


class UnsupportedFormatError(Exception):
    pass


class DocumentExtractor:

    SUPPORTED = {".pdf", ".docx", ".txt"}

    def detect_format(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        mapping = {".pdf": "pdf", ".docx": "docx", ".txt": "txt"}
        return mapping.get(ext, "unknown")

    def extract(self, file_path: str) -> Tuple[str, dict]:
        """
        Ritorna (testo_normalizzato, metadata).
        metadata: filename, extension, word_count
        Raises UnsupportedFormatError se il formato non è supportato.
        """
        fmt = self.detect_format(file_path)
        if fmt == "unknown":
            ext = Path(file_path).suffix.lower()
            raise UnsupportedFormatError(
                f"Formato non supportato: '{ext}'. Supportati: {self.SUPPORTED}"
            )

        path = Path(file_path)
        logger.debug(f"Estrazione {fmt}: {path.name}")

        if fmt == "pdf":
            text = self._extract_pdf(path)
        elif fmt == "docx":
            text = self._extract_docx(path)
        else:
            text = self._extract_txt(path)

        text = self._normalize(text)

        metadata = {
            "filename": path.name,
            "extension": path.suffix.lower(),
            "word_count": len(text.split()),
        }
        return text, metadata

    # ------------------------------------------------------------------
    # Estrattori per formato
    # ------------------------------------------------------------------

    def _extract_pdf(self, path: Path) -> str:
        try:
            return pdf_extract(str(path)) or ""
        except Exception as e:
            logger.error(f"Errore estrazione PDF {path.name}: {e}")
            return ""

    def _extract_docx(self, path: Path) -> str:
        try:
            doc = DocxDocument(str(path))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs)
        except Exception as e:
            logger.error(f"Errore estrazione DOCX {path.name}: {e}")
            return ""

    def _extract_txt(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            logger.error(f"Errore lettura TXT {path.name}: {e}")
            return ""

    # ------------------------------------------------------------------
    # Normalizzazione
    # ------------------------------------------------------------------

    def _normalize(self, text: str) -> str:
        """
        1. Rimuove hyphenation a fine riga (parola spezzata su più righe)
        2. Comprime whitespace multiplo in singolo spazio (preserva \n\n paragrafi)
        3. Strip globale
        """
        # 1. Hyphenation: "condi-\nzione" → "condizione"
        text = re.sub(r"-\n(\w)", r"\1", text)
        # 2. Preserva doppi newline (separatori di paragrafo)
        text = re.sub(r"\n{3,}", "\n\n", text)
        # 3. Comprimi spazi singoli (non newline) multipli
        text = re.sub(r"[ \t]+", " ", text)
        # 4. Spazio prima di newline
        text = re.sub(r" \n", "\n", text)
        return text.strip()
