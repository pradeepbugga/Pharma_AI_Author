from utils.llm import call_llm

def extract_active(drug_name, drug_candidates, text):
    prompt = f"""

    You are determining which candidate drugs are ACTIVE INGREDIENTS in a therapeutic context.

    Primary drug:
    {drug_name}

    Candidate drugs detected in the document:
    {drug_candidates}

    Context:
    {text}  

    Task:
    From the candidate drugs, identify which are ACTIVE INGREDIENTS.

    Definitions:
    - Active ingredients are drugs that are administered to produce a therapeutic effect
    - The primary drug is assumed to be active unless evidence contradicts this

    Rules:
    - Include a drug ONLY if there is explicit evidence it is administered (e.g., "treated with", "administered", "in combination with")
    - Exclude drugs that are:
    - comparators ("compared to", "versus")
    - screening panel drugs
    - mentioned as part of pathway discussion
    - not co-administered with the primary drug
    - Do NOT infer combinations unless explicitly stated

    Return JSON:
    {{
    "active_ingredients": ["..."],
    "rejected_candidates": {{
        "drug_name": "reason for exclusion"
    }},
    "confidence": 0-1
    }}
    """
    return call_llm(prompt)
