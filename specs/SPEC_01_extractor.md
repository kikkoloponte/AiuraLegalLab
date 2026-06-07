# SPEC 01 — Document Extractor (aiura_legal/ingestion/extractor.py)

```python
class DocumentExtractor:
    def extract(self, file_path: str) -> tuple[str, dict]:
        """(testo_normalizzato, metadata{filename,extension,word_count})"""
    def detect_format(self, file_path: str) -> str:
        """'pdf' | 'docx' | 'txt' | 'unknown'"""
```

Librerie: pdfminer.six (PDF), python-docx (DOCX), built-in (TXT).
Normalizza: rimuovi hyphenation, comprimi whitespace, preserva paragrafi.

Test (fixtures sintetiche senza PII):
1. extract PDF, DOCX, TXT
2. UnsupportedFormatError per .xlsx
3. metadata con word_count
4. "condi-\nzione" → "condizione"
