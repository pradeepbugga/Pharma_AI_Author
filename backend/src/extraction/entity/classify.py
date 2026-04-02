from utils.llm import call_llm

# this script is used to disambiguate the identified entities from the NER step.
# it takes the entity, the context around the entity, and the evidence from external databases (e.g. PubChem, UniProt)
# to classify the entity into one of drug/protein/gene/cell_line/reagent/other.

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

Confidence scoring:
    - 1.0 (Definitive): Local context provides a functional verb AND external evidence matches (e.g., "administered X" + PubChem hit).
    - 0.8 (Strong): Clear local context but missing external confirmation OR clear external hit but ambiguous local usage.
    - 0.6 (Mixed): Entity appears in a list of both drugs and proteins (e.g., "treatment with X, Y, and Z" where Z is a known protein).
    - 0.4 (Ambiguous): Entity is an abbreviation with multiple meanings (e.g., "ACE" could be the protein or the drug class).
    - 0.2 (Conflict): External evidence says "Protein" but text says "dosed with X" (Potential novel drug or LLM error).

Return JSON:
{{
  "entity": "...",
  "label": "...",
  "confidence": 0-1,
  "reason": "one sentence justification based on context and evidence"
}}
"""
    return call_llm(prompt)