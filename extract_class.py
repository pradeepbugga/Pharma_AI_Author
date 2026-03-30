from utils.llm import call_llm

def extract_class_info(drug_name, text):
    prompt = f"""

    Extract the pharmacological class of the drug "{drug_name}" based on the following text from a biomedical manuscript:
    {text}

    Rules:
    - Identify the therapeutic modality (e.g., small molecule, antibody, mRNA, siRNA, gene therapy, cell therapy)
    - Return a mechanism-based class appropriate to that modality:
    - small molecule → "X inhibitor/agonist"
    - antibody → "anti-X monoclonal antibody"
    - mRNA → "mRNA therapeutic encoding X"
    - siRNA → "siRNA targeting X"
    - gene therapy → "AAV-mediated gene therapy for X"
    - cell therapy → "CAR-T targeting X"

    - Be specific
    - Do not return generic labels like "drug" or "biologic"
    - If not stated, return null

    Return JSON:
    {{ "class": "...", "modality": "...", "confidence": 0-1 }}
    """
    return call_llm(prompt)

def falsify_class_info(drug_name,drug_class, modality, non_abstract_text):
    prompt = f"""

    You are validating a pharmacological class WITHOUT relying on explicit labels like "inhibitor".


    Claim:
    "Drug {drug_name} is classified as {drug_class} with modality {modality}."

    Context:
    {non_abstract_text}

    Tasks:
    1. Based on mechanism described (binding, activity, selectivity), does this drug function as an inhibitor of KRAS G12D?
    2. Ignore explicit phrases like "inhibitor"
    3. Use only mechanistic evidence with specific phrases from the text

    Return JSON:
    {{
        "mechanistically_supported": true/false,
        "mechanism_evidence": "...",
        "confidence_adjustment": -1 to +1
        }}
    """
    return call_llm(prompt)



if __name__ == "__main__":
    drug_name = "MRTX1133"
