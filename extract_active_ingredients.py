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
    - Active ingredients are the drug substance(s) that constitute the investigational product
    - This typically includes ONLY the primary drug unless the study explicitly defines a fixed combination product

    Important:
    - Drugs used in combination experiments are NOT active ingredients
    - These are considered combination agents, not part of the investigational product

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
