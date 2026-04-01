from backend.src.utils.llm import call_llm

# this function is used to extract the active ingredients field 
# it takes in the identified drug name, the list of identified drug candidates (from NER and classification), and the text as context.

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

    Confidence scoring:
    - 1.0 (Definitive): The text explicitly defines the drug composition (e.g., "{drug_name} is a small molecule targeting X" or "{drug_name} is a co-formulation of A and B").
    - 0.8 (Strong): Clear administration of {drug_name} alone; other candidates are explicitly labeled as "comparators," "standard of care," or "combination partners."
    - 0.5 (Ambiguous): Multiple drugs are mentioned together frequently (e.g., "the A+B group") without clarifying if it is a single pill (FDC) or two separate injections.
    - 0.3 (Incidental): The candidate drug is mentioned in the background/introduction but lacks clear co-administration evidence with {drug_name}.
    - 0.1 (Error Prone): The candidate drug is actually a reagent, a cell line, or a protein target (e.g., "treated with {drug_name} to inhibit BRAF" — BRAF is not an active ingredient).

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
