from backend.src.utils.llm import call_llm

# this script is used to extract the study model (in vitro, in vivo, clinical) based on the text evidence.
# it takes in the drug name, the identified chunks that passed filter for model type keywords 
# and the text as context.  The output is useful for downstream extraction of fields such as administration and dose

def extract_model(drug_name, study_model_context):
    prompt = f"""

    Task:
    You are classifying experimental model types for a study involving the drug {drug_name}.

    Evidence:
    - In vitro: {study_model_context['in_vitro']}
    - In vivo: {study_model_context['in_vivo']}
    - Clinical: {study_model_context['clinical']}

    Choose one:
    - in_vitro (cell-based experiments)
    - in_vivo (animal studies)
    - clinical (human patients)
    - mixed (multiple of the above)

    Rules:
    - Only consider contexts where the drug is administered or tested
    - Ignore background mentions or references to other studies
   
    Only classify "clinical" if there is evidence of:
    - human patients receiving treatment
    - clinical trials

    Do NOT classify as clinical for:
    - "patients" mentioned in discussion
    - "therapeutic potential"
    - "clinical relevance"

    Confidence Scoring:
    - 1.0 (Certain): The text explicitly describes a new experiment with {drug_name} (e.g., "We treated mice with...", "Cells were incubated...").
    - 0.7 (High): The text shows clear experimental data/results for {drug_name} but the methodology is in a different chunk.
    - 0.5 (Moderate): Mention of {drug_name} alongside a model, but phrasing is ambiguous (e.g., {drug_name} is a potent inhibitor in xenografts" without saying "We used...").
    - 0.2 (Low): Mention is likely a citation or a general statement (e.g., "inhibitors are often tested in cell lines").
    - 0.0 (None): No evidence found.

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

