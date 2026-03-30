from utils.llm import call_llm

def detect_model(drug_name, in_vitro_chunks, in_vivo_chunks, clinical_chunks):
    prompt = f"""

    Task:
    You are classifying experimental model types for a study involving the drug {drug_name}.

    Evidence:
    - In vitro: {in_vitro_chunks}
    - In vivo: {in_vivo_chunks}
    - Clinical: {clinical_chunks}

    Choose one:
    - in_vitro (cell-based experiments)
    - in_vivo (animal studies)
    - clinical (human patients)
    - mixed (multiple of the above)

    Rules:
    - Only consider contexts where the drug is administered or tested
    - Ignore background mentions or references to other studies

    For evidence: 
    Extract EXACT sentences from the text that support the mechanism.
    Do NOT summarize.
    Return verbatim quotes only.


    Return JSON:
    {{
    "model_type": "in_vitro | in_vivo | clinical | mixed | unknown",
    "components": ["in_vitro", "in_vivo", "clinical"],
    "has_clinical": true/false,
    "evidence": {{
        "in_vitro": "...",
        "in_vivo": "...",
        "clinical": "..."
    }},
    "confidence": 0-1
    }}
    """
    return call_llm(prompt)



if __name__ == "__main__":
    drug_name = "MRTX1133"
