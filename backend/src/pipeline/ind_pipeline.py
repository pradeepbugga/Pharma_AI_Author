import json

from backend.src.synthesize.synthesize_ind_intro import synthesize_preclinical, synthesize_clinical

from backend.src.ingest.section_parser import parse_sections
from backend.src.pipeline.main_pipeline import run_pipeline
from backend.src.pipeline.drug_pipeline import run_drug_pipeline
from backend.src.pipeline.study_pipeline import run_study_pipeline
from backend.src.synthesize.ind_fields import build_ind_fields


PAPER_PATH = "./backend/src/data/papers/PMID_36216931/raw_text.json"
ENTITY_COUNTS_PATH = "./extracted_entities.json"

def run_ind_pipeline(entity_counts, paper_path):

    entities = list(entity_counts.keys())

    # Load manuscript text (your JSON file)
    with open(paper_path) as f:
        data = json.load(f)

    sections = parse_sections(data)
  
    # -----ENTITY PIPELINE-----
    result = run_pipeline(entities, sections['abstract'] + sections['results'])

    print("\n=== ENTITY PIPELINE RESULT ===")

    primary_drug = result["primary_drug"]["primary_drug"]

    print(f"Primary drug identified: {primary_drug}")

    

    # ----DRUG PIPELINE -----
    drug_info = run_drug_pipeline(primary_drug, result, sections)

    print("\n=== DRUG PIPELINE RESULT ===")
    print(json.dumps(drug_info, indent=2))

    # ----STUDY PIPELINE -----
    study_info = run_study_pipeline(primary_drug, sections)

    print("\n=== STUDY PIPELINE RESULT ===")
    print(json.dumps(study_info, indent=2))

    # ----COMBINE RESULTS ----

    ind_context = {
        "drug_name": result["primary_drug"], 
        **drug_info,
        **study_info
    }

    print("\n=== COMPILED IND CONTEXT ===")

    fields = build_ind_fields(ind_context)


    print(json.dumps(fields, indent=2))
    # ----- SYNTHEIZE IND-INTRO -----

    print("\n=== SYNTHESIZED IND-INTRO STATEMENT ===")

    has_human_data = study_info.get("administration", {}).get("clinical", {}).get("value", False) 
     
    print(f"Has human data: {has_human_data}")

    ind_study_context = {
        "model_type": study_info.get("study_model", {}).get("model_type"),
        "models": study_info.get("study_model", {}).get("components", []),
        "has_clinical": has_human_data,
    }

    if has_human_data:
        ind_intro = synthesize_preclinical(fields, ind_study_context)
    else:
        ind_intro = synthesize_clinical(fields, ind_study_context)
    print(ind_intro)
   
    return fields, ind_intro, has_human_data

if __name__ == "__main__":
    run_ind_pipeline(ENTITY_COUNTS_PATH, PAPER_PATH)