from utils.llm import call_llm

#  this script takes the extracted fields and synthesizes them into an 
#  IND style introductory statement via LLM. 


def synthesize_intro(fields, study_context):
    prompt = f"""
    Write an IND-style introductory statement.

    IND-intro instructions:
    A brief introductory statement giving the name of the drug and all active ingredients, 
    the drug's pharmacological class, the structural formula of the drug (if known), the formulation of the dosage form(s) to be used, 
    the route of administration, and the broad objectives and planned duration of the proposed clinical investigation(s).

    You MUST use ONLY the provided structured data.
    You MUST NOT invent or infer any missing information.

    INPUT DATA:

    Drug Name:
    {fields.get("Drug Name", {}).get("value", "N/A")}

    Active Ingredients:
    {fields.get("Active Ingredients", {}).get("value", "N/A")}

    Pharmacological Class:
    {fields.get("Pharmacological Class", {}).get("value", "N/A")}

    Structural Formula:
    {fields.get("Structural Formula", {}).get("value", "N/A")}

    Formulation:
    {fields.get("Formulation", {}).get("value", "N/A")}

    Dose:
    {fields.get("Dose", {}).get("value", "N/A")}

    Route of Administration:
    {fields.get("Route of Administration", {}).get("value", "N/A")}

    Planned Exposure (Duration):
    {fields.get("Duration", {}).get("value", "N/A")}

    Objective:
    {fields.get("Broad Objectives", {}).get("value", "N/A")}

    Context on study model:
    {study_context}

    REQUIREMENTS:

    1. Write a single cohesive paragraph (3–7 sentences max)
    2. Include ALL provided fields
    3. Use formal scientific/regulatory tone
    4. If a field is missing, omit it (do NOT guess)
    5. Do NOT repeat information
    6. Do NOT include excessive mechanistic detail
    7. Do NOT hallucinate formulation, dose, or duration

    STYLE:

    - Start with drug identity and class
    - Then describe formulation and route
    - Then dose and exposure (if available)
    - End with study objective

    OUTPUT:
    Return ONLY the paragraph as string in JSON format:
    {{
    "ind_intro": "..."
    }}
    """

    return call_llm(prompt)



#  this function is for testing the control of directly generating the IND intro 
#  from the paper text without structured extraction.  We will notice that 
#  this strategy is prone to hallucination.  

def control_synthesis(text):
    prompt = f"""
    Write an IND-style introductory statement.

    IND-intro instructions:
    A brief introductory statement giving the name of the drug and all active ingredients, 
    the drug's pharmacological class, the structural formula of the drug (if known), the formulation of the dosage form(s) to be used, 
    the route of administration, and the broad objectives and planned duration of the proposed clinical investigation(s).

    You MUST use ONLY the provided structured data.
    You MUST NOT invent or infer any missing information.

    paper text:
    {text}

    REQUIREMENTS:

    1. Write a single cohesive paragraph (3–7 sentences max)
    2. Include ALL provided fields
    3. Use formal scientific/regulatory tone
    4. If a field is missing, omit it (do NOT guess)
    5. Do NOT repeat information
    6. Do NOT include excessive mechanistic detail
    7. Do NOT hallucinate formulation, dose, or duration

    STYLE:

    - Start with drug identity and class
    - Then describe formulation and route
    - Then dose and exposure (if available)
    - End with study objective

    OUTPUT:
    Return ONLY the paragraph as string in JSON format:
    {{
    "ind_intro": "..."
    }}
    """
    return call_llm(prompt)


# this is a test function to run the synthesis with the structured fields as input
# without having to run the entire extraction pipeline.  

if __name__ == "__main__":
    fields = {
  "Drug Name": {
    "value": "MRTX1133",
    "status": "present",
    "source": "text_extraction"
  },
  "Pharmacological Class": {
    "value": "KRAS<sup>G12D</sup> inhibitor",
    "status": "present",
    "source": "llm derived"
  },
  "Structural Formula": {
    "value": "C33H31F3N6O2",
    "status": "present",
    "source": "pubchem"
  },
  "Active Ingredients": {
    "value": [
      "MRTX1133"
    ],
    "status": "present",
    "source": "llm derived"
  },
  "Formulation": {
    "value": "MRTX1133 was dissolved in vehicle consisting of 10% Captisol in 50 mM citrate buffer pH 5.0 for intraperitoneal administration.",
    "status": "present",
    "source": "Mice were treated by IP injection with either vehicle consisting of 10% research grade Captisol (CyDex Pharmaceuticals, KS) in 50 mM citrate buffer pH 5.0 or MRTX1133 in vehicle at indicated doses."
  },
  "Dose": {
    "value": "3\u201330 mg/kg (BID (twice daily))",
    "status": "present",
    "source": "Route: intraperitoneal | Evidence: MRTX1133 was administered at 3, 10 and 30 mg/kg dose levels via intraperitoneal (IP) injection to achieve sufficient systemic plasma exposure in mice."
  },
  "Route of Administration": {
    "value": {
      "standard": "intraperitoneal",
      "abbreviation": "IP",
      "raw": "intraperitoneal (IP) injection"
    },
    "status": "present",
    "source": "MRTX1133 was administered at 3, 10 and 30 mg/kg dose levels via intraperitoneal (IP) injection to achieve sufficient systemic plasma exposure in mice."
  },
  "Duration": {
    "value": "28 days",
    "status": "present",
    "source": "[administration_duration] 28 days: MRTX1133 was well-tolerated at dose levels administered IP at up to 30 mg/kg twice daily (BID) in repeat-dose studies for up to 28 days with no evidence of weight loss or overt signs of toxicity. | [administration_duration] 7 days: X1133 also demonstrated dose-dependent inhibition of pERK in tumor lysates at 1 hour post last dose in the BID \u00d7 7 Days cohorts | [dosing_count] 3 consecutive doses: MRTX1133 administered IP for 3 consecutive doses at 12-hour intervals | [dosing_schedule] 2 days on / 5 days off: 30 mg/kg BID intermittent schedule of 2 treatment days followed by 5 days off | [measurement_timepoint] 3-day: a 3-day combination viability screen was conducted in vitro"
  },
  "Broad Objectives": {
    "value": "To evaluate MRTX1133, a non-covalent small-molecule KRASG12D inhibitor, for selective targeting of KRASG12D-mutant pancreatic ductal adenocarcinoma and colorectal cancer models, assessing tumor regression and downstream ERK signaling inhibition as primary endpoints.",
    "status": "present",
    "source": "llm_summary"
  }
}
    study_context={
        "model_type": "mixed",
        "models": [
            "in vitro",
            "in vivo"
        ],
        "has_clinical": False
    }


    intro = synthesize_intro(fields, study_context)
    print(intro)