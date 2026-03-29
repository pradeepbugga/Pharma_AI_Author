from utils.llm import call_llm


def classify_entity(entity, contexts, evidence):
    prompt = f"""
You are a biomedical entity classifier.

Entity: {entity}

Context:
{contexts}

External evidence:
{evidence}

Classify into one of:
[drug, protein, gene, cell_line, reagent, other]

Rules:
- Use context FIRST
- PubChem hit does NOT automatically mean drug
- Solvents like DMSO → reagent
- Proteins (UniProt) → protein

Return JSON:
{{
  "entity": "...",
  "label": "...",
  "confidence": 0-1
}}
"""
    return call_llm(prompt)