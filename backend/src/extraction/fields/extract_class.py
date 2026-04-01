from utils.llm import call_llm


# this function extracts the drug class based on the mechanism of action described in the text, without relying on explicit labels. 
#  It also returns a confidence score for how well supported the class is based on the text.
# we use the identified drug name and the abstract text as context

def extract_class_info(drug_name, abstract_text):
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

# this function takes the extracted class info and tries to falsify it 
# by looking for mechanistic evidence in the results section

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

    Extract EXACT sentences from the text that support the mechanism.
    Do NOT summarize.
    Return verbatim quotes only.

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
