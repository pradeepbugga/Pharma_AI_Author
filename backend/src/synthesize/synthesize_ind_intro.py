from backend.src.utils.llm import call_llm

#  this script takes the extracted fields and synthesizes them into an 
#  IND style introductory statement via LLM. 


def synthesize_preclinical(fields, study_context):
    prompt = f"""
    Write a preclinical investigational drug summary suitable for inclusion in an IND.

    IND-intro instructions:
    A brief introductory statement describing the investigational drug, including:
    - drug name and active ingredient(s)
    - pharmacological class
    - structural formula (if known)
    - formulation
    - route of administration
    - dose and exposure
    - study objective

    IMPORTANT:
    - You MUST follow the provided study context, not assume a clinical study
    - You MUST use ONLY the provided structured data.
    - You MUST NOT invent or infer any missing information.

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


def synthesize_clinical(fields, study_context):
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
    "source": "llm derived",
    "additional_info": "Confidence: 1.0"
  },
  "Pharmacological Class": {
    "value": "KRAS<sup>G12D</sup> inhibitor",
    "status": "present",
    "source": "llm derived",
    "additional_info": "Modality: small molecule | Evidence: MRTX1133 demonstrated binding to the GDP-bound, inactive form of KRAS$^{\\mathrm{G12D}}$ with an IC$_{50} < 2$ nM... MRTX1133 also inhibited the binding of a RAF-RAS binding domain (RBD) peptide to the active form of KRAS$^{\\mathrm{G12D}}$ with an IC$_{50}$ of 9 nM... binding of MRTX1133 to KRAS$^{\\mathrm{G12D}}$ resulted in a conformational change of Switch I and Switch II... MRTX1133 binding, independent of nucleotide state, eliminates KRAS$^{\\mathrm{G12D}}$ protein surface competency for binding effector proteins... MRTX1133 potently and selectively inhibits KRAS-dependent signaling and viability in the vast majority of KRAS$^{\\mathrm{G12D}}$-mutant cancer cell lines."
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
    "source": "llm derived",
    "additional_info": "Confidence: 1.0"
  },
  "Formulation": {
    "value": "MRTX1133 was dissolved in vehicle consisting of 10% Captisol in 50 mM citrate buffer pH 5.0 for intraperitoneal administration.",
    "status": "present",
    "source": "llm derived",
    "additional_info": "Evidence: Mice were treated by IP injection with either vehicle consisting of 10% research grade Captisol (CyDex Pharmaceuticals, KS) in 50 mM citrate buffer pH 5.0 or MRTX1133 in vehicle at indicated doses. | Confidence: 1.0"
  },
  "Dose": {
    "value": "3\u201330 mg/kg (BID (twice daily))",
    "status": "present",
    "source": "llm derived",
    "additional_info": "Evidence: MRTX1133 was administered at 3, 10 and 30 mg/kg dose levels via intraperitoneal (IP) injection to achieve sufficient systemic plasma exposure in mice (Fig.~S3A) and demonstrated complete pERK inhibition at both 1 and 6 hours post-dose in cancer cells using immunohistochemistry supplemented with an image analysis algorithm designed to evaluate the fraction of biomarker-positive tumor cells (Fig.~2A). | Confidence: 1.0"
  },
  "Route of Administration": {
    "value": {
      "standard": "intraperitoneal",
      "abbreviation": "IP",
      "raw": "intraperitoneal (IP)"
    },
    "status": "present",
    "source": "llm derived",
    "additional_info": "Evidence: MRTX1133 was administered at 3, 10 and 30 mg/kg dose levels via intraperitoneal (IP) injection to achieve sufficient systemic plasma exposure in mice (Fig.~S3A) and demonstrated complete pERK inhibition at both 1 and 6 hours post-dose in cancer cells using immunohistochemistry supplemented with an image analysis algorithm designed to evaluate the fraction of biomarker-positive tumor cells (Fig.~2A). | Confidence: 1.0"
  },
  "Duration": {
    "value": "28 days to 7 days",
    "status": "present",
    "source": "llm_derived",
    "additional_info": "Evidence: [administration_duration] 7 days: pERK recovery was observed by the 12-hour timepoint at each dose level after BID \u00d7 7 Days cohorts | [administration_duration] 28 days: After 28 days of administration, MRTX1133 administered at 30 mg/kg BID demonstrated significant anti-tumor activity... | [dosing_schedule] 2 days on / 5 days off: In the LS180 CRC model, MRTX1133 anti-tumor activity was explored using a 30 mg/kg BID intermittent schedule of 2 treatment days followed by 5 days off. | [dosing_count] 3 consecutive doses: MRTX1133 at 3, 10 or 30 mg/kg administered IP for 3 consecutive doses at 12-hour intervals | [measurement_timepoint] 3-day: a 3-day combination viability screen was conducted in vitro"
  },
  "Broad Objectives": {
    "value": "To evaluate MRTX1133, a non-covalent small-molecule KRASG12D inhibitor, for selective anti-tumor activity and regression in KRASG12D-mutant pancreatic ductal adenocarcinoma and colorectal cancer models.",
    "status": "present",
    "source": "llm_derived"
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

   


    intro = synthesize_preclinical(fields, study_context)
    print(intro)