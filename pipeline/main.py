import json
import requests

from utils.context import get_entity_context
from pipeline.evidence import gather_evidence
from pipeline.postprocess import extract_drug_candidates

from agents.disambiguate import classify_entity
from agents.select_primary import select_primary_drug
from schemas.evidence import normalize_evidence, enforce_db_rules
from agents.llm_canonicalize import canonicalize_entity

def compute_evidence_used(evidence):
    return {
        "pubchem": evidence["pubchem"]["compound"],
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

    normalized_entities = []
    for entity in entities:

        # canonicalize entity name to improve lookup success (e.g. "KRAS-WT" → "KRAS wild-type")

        original_name = entity
        res = canonicalize_entity(original_name)
        entity = res.get("canonical", original_name)
        print(f"Canonicalized entity: {entity} from original: {original_name}")

        if entity in normalized_entities:
            print(f"Skipping duplicate entity after normalization: {entity}")
            continue

        normalized_entities.append(entity)


        contexts = get_entity_context(entity, text)

        raw_evidence = gather_evidence(entity, session)
        
        evidence = normalize_evidence(raw_evidence)


        result = classify_entity(entity, contexts, evidence)
               
        result = validate_and_attach(result, entity, evidence)

        result = enforce_db_rules(result, evidence)

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