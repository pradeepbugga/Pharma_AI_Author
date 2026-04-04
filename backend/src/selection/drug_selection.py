from backend.src.utils.llm import call_llm

# this script is used to select the primary drug being studied in the manuscript from the list of drug candidates identified from the NER step.
# it takes in the drug candidates and the text of the manuscript as context to make the decision


# this function first extracts the drug candidates to pass into below function
def extract_drug_candidates(classified_entities):
    return [
        e["entity"]
        for e in classified_entities
        if e["label"] == "drug"
    ]


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

Confidence Scoring:
    - 1.0 (Definitive): The drug is named in the TITLE and used in the majority of experiments as the main variable.
    - 0.8 (Strong): Clear distinction between a "test" drug and "standard of care" (e.g., "We compared DrugX to Paclitaxel"). DrugX is Primary.
    - 0.5 (Co-Primary): Two drugs are studied equally (e.g., a head-to-head comparison where neither is "ours").
    - 0.3 (Ambiguous): A screening paper where 50 drugs are mentioned; none are highlighted as the "primary" focus.
    - 0.1 (Error): Only a vehicle or a known reference drug is mentioned; no new investigational product is identified.

Return JSON:
{{
  "primary_drug": "...",
  "secondary_drugs": [...],
  "evidence": "Text snippets supporting the selection",
  "confidence": 0-1
}}
"""
    return call_llm(prompt)