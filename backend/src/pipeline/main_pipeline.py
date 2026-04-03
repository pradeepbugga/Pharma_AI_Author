from backend.src.pipeline.entity_pipeline import run_entity_pipeline
from backend.src.selection.drug_selection import extract_drug_candidates
from backend.src.selection.drug_selection import select_primary_drug

def run_pipeline(entities, text):
    print("=== PASS 1: ENTITY PROCESSING ===")

    classified_entities = run_entity_pipeline(entities, text)

    print("\n=== PASS 2: DRUG SELECTION ===")

    drug_candidates = extract_drug_candidates(classified_entities)
    print("\nDrug candidates:", drug_candidates)

    primary = select_primary_drug(drug_candidates, text)
    print("\nPrimary drug:", primary)

    return {
        "classified_entities": classified_entities,
        "drug_candidates": drug_candidates,
        "primary_drug": primary
    }

