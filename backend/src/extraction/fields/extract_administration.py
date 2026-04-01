from backend.src.utils.llm import call_llm

# this script is used to extract the administration information for the identified drug.
# it takes in the drug name, the identified chunks that passed filter for administration keywords as context
# the chunks for the study model (i.e. in vitro / invivo / clinical chunks) 
# and the context that is output of extract_study_model 

def extract_admin(drug_name, admin_chunks, model_chunks, study_context_memory):
    prompt = f"""

    You are identifying ALL contexts in which a drug is administered.

    Drug:
    {drug_name}

    Explicit administration snippets:
    {admin_chunks}

    Model context snippets (may imply administration):
    {model_chunks}

    Context Memory:
    The study includes: {context_memory}

    Important:
    - Explicit snippets contain administration verbs (e.g., "treated with")
    - Model snippets may describe outcomes (e.g., tumor regression)

    Task:
    Determine whether the drug is administered in:

    1. In vitro
    2. In vivo
    3. Clinical

    Rules:
    - If explicit snippets show administration → evidence_type = "explicit"
    - If only model/context snippets imply administration → evidence_type = "inferred"
    - Outcome-only statements (inhibition, regression) → inferred
    - Do NOT treat inferred evidence as explicit
    - PDX → in vivo, not clinical


    Confidence scoring:
    1.0 (Certain): The text explicitly names the drug, the dose/concentration, and the specific model (e.g., "Mice were treated with 30mg/kg MRTX1133").
    0.8 (High): The text describes a clear result of the drug in a specific model, but the exact administration details are in a different snippet.
    0.5 (Medium): The drug is mentioned in the same paragraph as a model, but the connection is vague or the evidence is heavily "inferred" from secondary outcomes.
    < 0.3 (Low): The snippet mentions the drug and the model type (e.g., "xenograft") but in a general context (e.g., "Future studies should look at xenografts").


    Return JSON:
    {{
    "in_vitro": {{
        "value": true/false,
        "evidence_type": "explicit | inferred | none",
        "evidence": "...",
        "confidence": 0-1
    }},
    "in_vivo": {{
        "value": true/false,
        "evidence_type": "explicit | inferred | none",
        "evidence": "...",
        "confidence": 0-1
    }},
    "clinical": {{
        "value": true/false,
        "evidence_type": "explicit | inferred | none",
        "evidence": "...",
        "confidence": 0-1
    }},
    "confidence": 0-1
    }}
    """

    return call_llm(prompt)

