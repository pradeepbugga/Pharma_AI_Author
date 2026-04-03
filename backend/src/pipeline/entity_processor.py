from backend.src.extraction.entity.canonicalize import canonicalize_entity
from backend.src.extraction.entity.classify import classify_entity
from backend.src.utils.context import get_entity_context
from backend.src.evidence.format import compute_evidence_used
from backend.src.evidence.gather import gather_evidence
from backend.src.evidence.normalize import normalize_evidence
from backend.src.validation.entity_validation import enforce_db_rules, validate_and_attach

# this script is responsible for processing the extracted entities, 
# gathering evidence for them from database APIs, and classifying them 

def process_entity(entity, text, session):
    
    original_name = entity

    # canonicalize entity name to improve lookup success 
    res = canonicalize_entity(original_name)
    entity = res.get("canonical", original_name)
    
    # get context for entity
    contexts = get_entity_context(entity, text)

    # gather evidence from databases
    raw_evidence = gather_evidence(entity, session)
    
    # normalize evidence into a consistent format for classification
    evidence = normalize_evidence(raw_evidence)

    # classify entity based on evidence and context
    result = classify_entity(entity, contexts, evidence)
               
    # validate result format and attach evidence
    result = validate_and_attach(result, entity, evidence)

    # enforce any database-driven rules (e.g. if Cellosaurus evidence strongly indicates a cell line, classify as cell line)
    result = enforce_db_rules(result, evidence)


    result["evidence_used"] = compute_evidence_used(evidence)

    return entity, result
