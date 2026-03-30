from utils.llm import call_llm

def detect_admin(drug_name, admin_chunks, context_memory):
    prompt = f"""

    You are identifying ALL contexts in which a drug is administered.

    Drug:
    {drug_name}

    Context:
    {admin_chunks}

    Context Memory:
    Previous analysis determined the study models are {context_memory}.

    Important:
    - These are ALL known administration-related snippets
    - Some may correspond to different experimental settings


    Task:
    Determine whether the drug is administered in each of the following:

    1. In vitro (cell-based treatment)
    2. In vivo (animal studies)
    3. Clinical (human patients)

    Rules:
    - A category is TRUE only if there is clear evidence of treatment/administration
    - "cells treated with" → in vitro
    - "mice treated with", "xenograft" → in vivo
    - "patients", "clinical trial" → clinical
    - Binding assays or biochemical assays → NOT administration

    - You MUST consider ALL snippets collectively
    - Do NOT rely on a single snippet
    - If multiple types are present → mark all as true


    For evidence: 
        Extract EXACT sentences from the text that support the mechanism.
        Do NOT summarize.
        Return verbatim quotes only.


    Return JSON:
    {{
    "in_vitro": true/false,
    "in_vivo": true/false,
    "clinical": true/false,
    "evidence": {{
        "in_vitro": "...",
        "in_vivo": "...",
        "clinical": "..."
    }},
    "confidence": 0-1
    }}
    """
    return call_llm(prompt)

