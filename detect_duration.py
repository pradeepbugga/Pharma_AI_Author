import re
from utils.llm import call_llm
from detect_dose import get_context

DURATION_PATTERNS = [
    r"\d+\s+days",
    r"\d+-day",
    r"\d+\s+weeks",
    r"up to\s+\d+\s+days",
    r"after\s+\d+\s+days",
    r"\d+\s+consecutive\s+doses",
    r"bid\s*[×x]\s*\d+\s+days",
    r"\d+\s+days\s+off",
    r"\d+\s+days\s+on"
]

def extract_duration_candidates(text):
    matches = []

    for pattern in DURATION_PATTERNS:
        matches += re.findall(pattern, text, re.IGNORECASE)

    return list(set(matches))


def get_duration_contexts(text, candidates):
    results = []

    for c in candidates:
        ctx = get_context(text, c, window=120)
        results.append({
            "value": c,
            "context": ctx
        })

    return results



def detect_duration_LLM(drug_name, duration_candidates, duration_context, admin_chunks, context_memory_administration, context_memory_dosage):
    prompt = f"""

    You are validating in vivo dosing information for a drug.

    Drug:
    {drug_name}

    Candidate durations:
    {duration_candidates}

    Duration contexts:
    {duration_context}

    Administration snippets:
    {admin_chunks}

    Context (from administration detection):
    {context_memory_administration}

    Context (from dose detection):
    {context_memory_dosage}

    Task:
    Determine if this represents:

    - in_vivo_duration (treatment duration in animals)
    - clinical_duration (treatment duration in humans)
    - in_vitro_timepoint (cell exposure time, NOT treatment duration)
    - measurement_timepoint (e.g., time after dosing)
    - unclear

    Rules:
    - "for X days/weeks" in animal dosing → in_vivo_duration
    - "3-hour treatment", "24 h incubation" → in_vitro_timepoint
    - Timepoints after dosing → measurement_timepoint
    - Prefer conservative classification

    Return JSON:
    {{
      "classification": "...",
      "confidence": 0-1,
      "reason": "..."
    }}
    """

    return call_llm(prompt)

