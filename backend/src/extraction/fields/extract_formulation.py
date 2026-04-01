from backend.src.utils.llm import call_llm

# this function is used to extract the formulation information for the identified drug.
# it takes in the drug name and the identified chunks that passed filter for formulation keywords as context

def extract_formulation(drug_name, formulation_chunks):
    prompt = f"""

    You are a pharmaceutical formulation expert

    Drug:
    {drug_name}

    Explicit formulation snippets:
    {formulation_chunks}
    

    Task:
    Identify formulation details, including:

    - vehicle (e.g., DMSO, PEG, saline)
    - excipients (co-solvents, stabilizers)
    - preparation (e.g., dissolved, diluted)

    Rules:
    - Only extract explicitly stated information
    - Do NOT infer missing components
    - Do NOT hallucinate standard formulations


    Confidence scoring:
    - 1.0 (Certain): Complete recipe provided with exact percentages/ratios (e.g., "10% DMSO, 40% PEG300, 5% Tween-80, and 45% saline").
    - 0.8 (High): Vehicle and all components are named, but exact percentages/ratios are missing.
    - 0.6 (Medium): Only the primary vehicle is named (e.g., "dissolved in 0.5% methylcellulose") without mentioning co-solvents.
    - 0.4 (Low): Vague mention of a "standard vehicle" or "prepared as previously described [citation]" without providing the details.
    - 0.0 (Invalid): No formulation data found or the text describes the *in vitro* assay buffer (e.g., "diluted in culture medium") instead of the *in vivo* dose formulation.

    Return JSON:
        {{
      "vehicle": "...",
      "excipients": [...],
      "formulation_description": "...",
      "status": "present | partial | missing",
      "evidence": "exact sentence",
      "confidence": 0-1
    }}
    """

    return call_llm(prompt)

