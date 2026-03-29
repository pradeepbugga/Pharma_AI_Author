from utils.llm import call_llm


def select_primary_drug(drug_candidates, text):
    prompt = f"""
You are analyzing a biomedical manuscript.

Drug candidates:
{drug_candidates}

Text:
{text[:3000]}

Identify:
- the PRIMARY drug being studied
- any secondary/comparator drugs

Focus on:
- which compound is central to experiments
- not solvents or background mentions

Return JSON:
{{
  "primary_drug": "...",
  "secondary_drugs": [...],
  "confidence": 0-1
}}
"""
    return call_llm(prompt)