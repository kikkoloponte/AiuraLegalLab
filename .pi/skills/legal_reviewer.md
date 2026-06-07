---
name: legal_reviewer
description: Verifica citazioni rule-based. Blocca risposte con fonti non nel Research Packet.
model: rule_based
temperature: 0.0
max_tokens: 512
---

# Legal Reviewer [S5]

Gatekeeper della qualità. Verifica meccanica del Citation Contract.
Principalmente rule-based — nessuna chiamata LLM per i check standard.

## Verifiche (in ordine)

1. **Citation Grounding**: ogni source_id nella risposta è nel Packet?
   → FAIL se anche un solo source_id non trovato

2. **Vigenza temporale**: norma vigente alla data di riferimento?
   → WARN se norma modificata/abrogata prima della data

3. **Contrasti non dichiarati**: Packet ha edge CONTRASTA e la risposta li ignora?
   → WARN

4. **Incostituzionalità**: norma con stato=INCOSTITUZIONALE citata come vigente?
   → FAIL CRITICO

## Output

```json
{
  "verdict": "PASS|FAIL|WARN",
  "checks": {
    "citation_grounding": "PASS",
    "temporal_validity": "PASS",
    "conflict_disclosure": "PASS",
    "constitutionality": "PASS"
  },
  "ungrounded_citations": [],
  "warnings": [],
  "action": "DELIVER|RE_RETRIEVAL|BLOCK"
}
```
