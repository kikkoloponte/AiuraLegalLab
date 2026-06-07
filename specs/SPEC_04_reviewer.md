# SPEC 04 — Citation Reviewer (aiura_legal/core/reviewer/reviewer.py)

NESSUNA chiamata LLM — interamente rule-based.

```python
@dataclass
class ReviewResult:
    verdict: str  # "PASS" | "FAIL" | "WARN"
    checks: dict[str, str]
    ungrounded_citations: list[str]
    warnings: list[str]
    action: str   # "DELIVER" | "RE_RETRIEVAL" | "BLOCK"

class CitationReviewer:
    def verify(self, response_text: str,
               research_packet: ResearchPacket) -> ReviewResult: ...
    def extract_citations(self, text: str) -> list[str]: ...
```

Pattern citazioni da estrarre:
  CC_ART_\d+, CP_ART_\d+, CPP_ART_\d+,
  CASS_(?:PEN|CIV|SS_UU)_\d{4}_\d+,
  CEDU_\w+_\d{4}, COST_\d{4}_\d+

Test:
  1. PASS: citazioni tutte nel Packet
  2. FAIL: "CC_ART_999" non nel Packet
  3. WARN: norma con valid_to passata
  4. FAIL CRITICO: norma con stato=INCOSTITUZIONALE
  5. extract_citations() estrae correttamente da testo legale
