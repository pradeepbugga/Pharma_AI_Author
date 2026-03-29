import json
import requests

from utils.context import get_entity_context
from pipeline.evidence import gather_evidence
from pipeline.postprocess import extract_drug_candidates

from agents.disambiguate import classify_entity
from agents.select_primary import select_primary_drug


def run_pipeline(entities, text):
    session = requests.Session()

    classified_entities = []

    print("=== PASS 1: DISAMBIGUATION ===")

    for entity in entities:
        contexts = get_entity_context(entity, text)

        evidence = gather_evidence(entity, session)

        result = classify_entity(entity, contexts, evidence)

        classified_entities.append(result)

        print("raw result:", result)
        label = result.get("label", "N/A")

        print(f"{entity} → {label}")

    # Step 2: filter drug candidates
    drug_candidates = extract_drug_candidates(classified_entities)

    print("\nDrug candidates:", drug_candidates)

    print("\n=== PASS 2: PRIMARY DRUG SELECTION ===")

    primary = select_primary_drug(drug_candidates, text)

    return {
        "classified_entities": classified_entities,
        "drug_candidates": drug_candidates,
        "primary_drug": primary
    }