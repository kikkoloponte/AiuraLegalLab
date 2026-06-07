"""
Test DocumentExtractor — fixtures sintetiche, zero PII.
"""
from __future__ import annotations
import io
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from aiura_legal.ingestion.extractor import DocumentExtractor, UnsupportedFormatError


@pytest.fixture
def extractor():
    return DocumentExtractor()


# ------------------------------------------------------------------
# detect_format
# ------------------------------------------------------------------

def test_detect_pdf(extractor):
    assert extractor.detect_format("documento.pdf") == "pdf"

def test_detect_docx(extractor):
    assert extractor.detect_format("atto.docx") == "docx"

def test_detect_txt(extractor):
    assert extractor.detect_format("nota.txt") == "txt"

def test_detect_unknown(extractor):
    assert extractor.detect_format("foglio.xlsx") == "unknown"

def test_detect_case_insensitive(extractor):
    assert extractor.detect_format("FILE.PDF") == "pdf"


# ------------------------------------------------------------------
# UnsupportedFormatError
# ------------------------------------------------------------------

def test_unsupported_format_raises(extractor, tmp_path):
    fake = tmp_path / "foglio.xlsx"
    fake.write_text("dati")
    with pytest.raises(UnsupportedFormatError, match="xlsx"):
        extractor.extract(str(fake))


# ------------------------------------------------------------------
# TXT extract
# ------------------------------------------------------------------

def test_extract_txt(extractor, tmp_path):
    f = tmp_path / "nota.txt"
    f.write_text("Articolo 1.\nIl contratto è valido.", encoding="utf-8")
    text, meta = extractor.extract(str(f))
    assert "Articolo 1" in text
    assert meta["extension"] == ".txt"
    assert meta["word_count"] > 0
    assert meta["filename"] == "nota.txt"


def test_extract_txt_word_count(extractor, tmp_path):
    f = tmp_path / "parole.txt"
    f.write_text("uno due tre quattro cinque", encoding="utf-8")
    text, meta = extractor.extract(str(f))
    assert meta["word_count"] == 5


# ------------------------------------------------------------------
# Normalizzazione
# ------------------------------------------------------------------

def test_normalize_hyphenation(extractor, tmp_path):
    """'condi-\nzione' → 'condizione'"""
    f = tmp_path / "hyph.txt"
    f.write_text("Le condi-\nzioni del contratto.", encoding="utf-8")
    text, _ = extractor.extract(str(f))
    assert "condizioni" in text
    assert "condi-" not in text

def test_normalize_whitespace(extractor, tmp_path):
    f = tmp_path / "ws.txt"
    f.write_text("testo   con   spazi   multipli", encoding="utf-8")
    text, _ = extractor.extract(str(f))
    assert "  " not in text

def test_normalize_preserves_paragraphs(extractor, tmp_path):
    f = tmp_path / "para.txt"
    f.write_text("Paragrafo uno.\n\nParagrafo due.", encoding="utf-8")
    text, _ = extractor.extract(str(f))
    assert "\n\n" in text


# ------------------------------------------------------------------
# PDF extract (mock pdfminer)
# ------------------------------------------------------------------

def test_extract_pdf_via_mock(extractor, tmp_path):
    fake_pdf = tmp_path / "atto.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4 fake")
    with patch(
        "aiura_legal.ingestion.extractor.pdf_extract",
        return_value="Testo estratto dal PDF sintetico.",
    ):
        text, meta = extractor.extract(str(fake_pdf))
    assert "PDF sintetico" in text
    assert meta["extension"] == ".pdf"


def test_extract_pdf_error_returns_empty(extractor, tmp_path):
    fake_pdf = tmp_path / "corrotto.pdf"
    fake_pdf.write_bytes(b"not a pdf")
    with patch(
        "aiura_legal.ingestion.extractor.pdf_extract",
        side_effect=Exception("parsing error"),
    ):
        text, meta = extractor.extract(str(fake_pdf))
    assert text == ""


# ------------------------------------------------------------------
# DOCX extract (mock python-docx)
# ------------------------------------------------------------------

def test_extract_docx_via_mock(extractor, tmp_path):
    fake_docx = tmp_path / "contratto.docx"
    fake_docx.write_bytes(b"PK fake docx content")

    mock_para1 = MagicMock()
    mock_para1.text = "Primo paragrafo sintetico."
    mock_para2 = MagicMock()
    mock_para2.text = "Secondo paragrafo sintetico."
    mock_doc = MagicMock()
    mock_doc.paragraphs = [mock_para1, mock_para2]

    with patch("aiura_legal.ingestion.extractor.DocxDocument", return_value=mock_doc):
        text, meta = extractor.extract(str(fake_docx))

    assert "Primo paragrafo" in text
    assert "Secondo paragrafo" in text
    assert meta["extension"] == ".docx"
