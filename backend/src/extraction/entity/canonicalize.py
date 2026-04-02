from utils.llm import call_llm


def canonicalize_entity(entity):
    prompt = f"""
You are a biomedical entity classifier.

Return a canonical form WITHOUT changing entity type.

Rules:
- If protein → keep protein (e.g., SHP2 stays SHP2, not PTPN11)
- If gene → keep gene
- If mutation → return base gene
- If drug → keep drug name unchanged
- If cell line → keep unchanged

If the entity is a pathway/protein family name:
map to the canonical gene symbol when appropriate.

Examples:
PI3Kalpha → PIK3CA
SHP2 → SHP2 (do not convert to PTPN11)


Entity: {entity}

Example: If entity is "KRAS-G12D", return {{"canonical": "KRAS"}}

Return JSON:
{{ "canonical": "...", "type": "gene | protein | drug | cell_line | reagent | other" }}
"""
    return call_llm(prompt)