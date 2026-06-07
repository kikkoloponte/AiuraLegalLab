# SPEC 02 — PII Anonymizer (aiura_legal/core/anonymizer/anonymizer.py)

```python
@dataclass
class AnonymizationResult:
    anonymized_text: str
    entity_map: dict[str, str]   # "[PERSONA_001]" → "Mario Rossi"
    stats: dict
    residual_pii_warnings: list[str]

class LegalAnonymizer:
    def anonymize(self, text: str, doc_id: str) -> AnonymizationResult: ...
    def restore(self, anonymized_text: str, entity_map: dict) -> str: ...
```

Layer 1 — Regex (implementa prima):
  CF: r"\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b"
  PIVA: r"(?:P\.?\s*IVA\s*)(\d{11})\b"
  IBAN: r"\bIT\d{2}[A-Z]\d{10}\d{12}\b"
  Email: r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b"
  Tel: r"(?:\+39\s?)?(?:0\d{1,4}[\s.-]?\d{6,8}|3\d{2}[\s.-]?\d{6,7})"

Layer 2 — spaCy it_core_news_lg:
  Entità PER, ORG con confidence > 0.80

CRITICO — NON anonimizzare:
  "art. 1218 c.c.", "D.Lgs. 231/2001", "Corte di Cassazione",
  "Comune di Milano", "Cass. Sez. III n. 12345/2023"

Test con dati SINTETICI (es. "Test Avvocato Uno", CF fittizio):
  1. CF regex → [CF_REDACTED]
  2. Email → [EMAIL_REDACTED]
  3. Persona spaCy → [PERSONA_001]
  4. "art. 1218 c.c." → invariato (no false positive)
  5. restore() → testo identico all'originale
