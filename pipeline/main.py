import json
import requests

from utils.context import get_entity_context
from pipeline.evidence import gather_evidence
from pipeline.postprocess import extract_drug_candidates

from agents.disambiguate import classify_entity
from agents.select_primary import select_primary_drug
from schemas.evidence import normalize_evidence


def compute_evidence_used(evidence):
    return {
        "pubchem": evidence["pubchem"]["compound"] or evidence["pubchem"]["substance"],
        "uniprot": evidence["uniprot"]["found"],
        "cellosaurus": evidence["cellosaurus"]["found"],
        "web": evidence["web"]["used"]
    }


def validate_and_attach(result, entity, evidence):
    if not isinstance(result, dict) or "label" not in result:
        return {
            "entity": entity,
            "label": "other",
            "confidence": 0.0,
            "evidence_used": {"pubchem": False, "uniprot": False, "cellosaurus": False, "web": False},
            "evidence": evidence
        }
    result["evidence"] = evidence
    return result

def run_pipeline(entities, text):
    session = requests.Session()

    classified_entities = []

    print("=== PASS 1: DISAMBIGUATION ===")

    for entity in entities:
        contexts = get_entity_context(entity, text)

        raw_evidence = gather_evidence(entity, session)
        evidence = normalize_evidence(raw_evidence)


        result = classify_entity(entity, contexts, evidence)
        
        result = validate_and_attach(result, entity, evidence)

        result["evidence_used"] = compute_evidence_used(evidence)

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