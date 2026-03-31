import re
from utils.llm import call_llm

DOSE_PATTERN = r"""
(\b\d+(\.\d+)?\s*
(mg/kg|mg|µg/kg|µM|nM|pM|mg/kg/day|mg/kg/day|mg/kg/week))
"""

def extract_dose_candidates(text):
    matches = re.findall(DOSE_PATTERN, text, re.IGNORECASE | re.VERBOSE)

    return [m[0] for m in matches]

def get_context(text, value, window=100):
    idx = text.lower().find(value.lower())
    if idx == -1:
        return ""

    start = max(0, idx - window)
    end = min(len(text), idx + window)
    return text[start:end]

def get_dose_contexts(text, candidates):
    results = []

    for c in candidates:
        ctx = get_context(text, c)
        results.append({
            "value": c,
            "context": ctx
        })
    return results

def split_by_unit(candidates):
    in_vivo = []
    in_vitro = []

    for c in candidates:
        if "mg/kg" in c:
            in_vivo.append(c)
        elif "nm" in c or "µm" in c or "pm" in c:
            in_vitro.append(c)

    return in_vivo, in_vitro

def summarize_dose_range(in_vivo_doses):
    values = []

    for d in in_vivo_doses:
        num = float(d.split()[0])
        values.append(num)

    return {
        "min": min(values),
        "max": max(values),
        "unit": "mg/kg"
    }


def detect_dose_LLM(drug_name, in_vivo_candidates, candidate_context, admin_chunks, context_memory):
    prompt = f"""

    You are validating in vivo dosing information for a drug.

    Drug:
    {drug_name}

    Candidate in vivo doses:
    {in_vivo_candidates}

    Candidate contexts:
    {candidate_context}

    Administration snippets:
    {admin_chunks}

    Context (from study):
    {context_memory}

    Task:
    1. Confirm that these values represent actual administered doses (not assay values)
    2. Identify whether they represent:
    - multiple dose levels
    - a dose range
    3. Extract the EXACT sentence describing dosing (if present)
    4. Identify route and frequency if mentioned

    Rules:
    - mg/kg in animal context → valid dose
    - Ignore nM / µM values
    - Do NOT invent values not present in the text

    CONFIDENCE SCORING RUBRIC:
    - 1.0 (Certain): The text explicitly links {drug_name}, a numeric mg/kg value, a route (e.g., Oral), and a frequency (e.g., BID).
    - 0.8 (High): The dose (mg/kg) and drug are clear, but the frequency or route must be inferred from the general methods section.
    - 0.6 (Medium): A dose is mentioned (e.g., "30 mg/kg"), but it's unclear if it was the dose *administered* or a dose *observed* in a citation.
    - 0.3 (Low): Only a range is mentioned without specific study details, or units are ambiguous.
    - 0.0 (Invalid): No mg/kg values found, or only in vitro (nM/µM) concentrations are present.


    Return JSON:
    {{
    "valid": true/false,
    "dose_type": "single | multiple | range",
    "dose_values": [...],
    "range": "X–Y mg/kg",
    "route": {{"standard": "...", "abbreviation": "...", "raw": "..."}},
    "frequency": "...",
    "evidence": "exact sentence",
    "confidence": 0-1
    }}
    """

    return call_llm(prompt)

