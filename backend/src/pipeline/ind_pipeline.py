import json
from pipeline.main import run_pipeline
from synthesize_ind_intro import synthesize_intro, control_synthesis

from backend.src.ingest.section_parser import parse_sections
from backend.src.pipeline.main_pipeline import run_pipeline
from backend.src.pipeline.drug_pipeline import run_drug_pipeline

PAPER_PATH = "./data/papers/PMID_36216931/raw_text.json"
ENTITY_COUNTS_PATH = "./extracted_entities.json"

def run_ind_pipeline(entity_counts_path, paper_path):

    # load entities 
    with open(entity_counts_path) as f:
        entity_counts = json.load(f)

    entities = list(entity_counts.keys())

    # Load manuscript text (your JSON file)
    with open(paper_path) as f:
        data = json.load(f)

    sections = parse_sections(data)

    # text is the main variable we use for pipeline (will define others as needed for specific steps)
    text = "".join(sections['abstract'] + sections['results'])


    # -----ENTITY PIPELINE-----
    result = run_pipeline(entities, text)

    #print("\n=== ENTITY PIPELINE OUTPUT ===")
    #print(json.dumps(result, indent=2))

    primary_drug = result["primary_drug"]["primary_drug"]
    #print(f"\nPrimary drug selected: {primary_drug}")

    # ----DRUG PIPELINE -----
    drug_info = run_drug_pipeline(primary_drug, result, sections)

    # ----STUDY PIPELINE -----
    study_info = run_study_pipeline(primary_drug, sections)

    # ----COMBINE RESULTS ----

    ind_context = {
        "drug_name": primary_drug, 
        **drug_info,
        **study_info
    }


def assign_status(value):
    if value is None:
        return "missing"
    if value == "not_applicable":
        return "not_applicable"
    return "present"

# build final output
fields = {}

fields["Drug Name"] = {
    "value": ind_context["drug_name"],
    "status": assign_status(ind_context["drug_name"]),
    "source": "text_extraction"
}

fields["Pharmacological Class"] = {
    "value": ind_context["pharmacological_class"].get("class"),
    "status": "present",
    "source": "llm derived"
}

fields["Structural Formula"] = {
    "value": ind_context["structural_formula"].get("value").get("molecular_formula") if ind_context["structural_formula"].get("value") else None,
    "status": "present" if ind_context["structural_formula"].get("value").get("molecular_formula") else "missing",
    "source": "pubchem"
}

fields["Active Ingredients"] = {
    "value": ind_context["active_ingredients"].get("active_ingredients"),
    "status": assign_status(ind_context["active_ingredients"].get("active_ingredients")),
    "source": "llm derived"
}   



fields["Formulation"] = {
    "value": ind_context["formulation"].get("formulation_description"),
    "status": ind_context["formulation"].get("status"),
    "source": ind_context["formulation"].get("evidence", "")
}   

# Assuming 'dose' is the dictionary from your "DOSE OUTPUT"
dose_output = ind_context["dose"]

# Extract unit safely (e.g., "mg/kg" from "3 mg/kg")
unit = dose_output["dose_values"][0].split()[-1] if dose_output["dose_values"] else ""

# Map to your fields object
fields["Dose"] = {
    # Use the pre-formatted range if it exists, otherwise join the list
    "value": f"{dose_output.get('range', 'N/A')} ({dose_output.get('frequency', '')})",
    "status": "present" if dose_output.get("valid") else "absent",
    "source": f"Route: {dose_output.get('route', {}).get('standard')} | Evidence: {dose_output.get('evidence', '')}"
}

fields["Route of Administration"] = {
    "value": ind_context["dose"].get("route"),  
    "status": "present",
    "source": ind_context["dose"].get("evidence", "")
}

def format_duration_field(normalized_output):
    # 1. Prioritize the main treatment duration (usually the longest or highest confidence)
    admin_durations = normalized_output.get("administration_duration", [])
    
    if admin_durations:
        # Sort by confidence or length (e.g., picking 28 days over 7 days)
        primary = max(admin_durations, key=lambda x: x['confidence'])
        main_value = primary['normalized_value']
    else:
        main_value = "Not specified"

    # 2. Combine all evidence across all categories for full traceability
    all_evidence = []
    for category, items in normalized_output.items():
        for item in items:
            all_evidence.append(f"[{category}] {item['normalized_value']}: {item['evidence']}")
    
    full_source = " | ".join(all_evidence)

    return {
        "value": main_value,
        "status": "present" if admin_durations else "absent",
        "source": full_source
    }

fields["Duration"] = format_duration_field(normalized_duration_results)

fields["Broad Objectives"] = {
    "value": ind_context["objectives"].get("objective"),
    "status": "present",
    "source": "llm_summary"
}


print("\n=== FINAL SYNTHESIZED IND-INTRO FIELDS ===")
print(json.dumps(fields, indent=2))

print("\n=== SYNTHESIZED IND-INTRO STATEMENT ===")
ind_intro = synthesize_intro(fields, study_model)
print(ind_intro)
'''