
# this script is used to validate the extracted entities and attach evidence to them.

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

# this function enforces hard rules based on database evidence, overriding the model's prediction if necessary.

def enforce_db_rules(result, evidence):
    if not isinstance(result, dict):
        return result

    if "label" not in result:
        return result  # skip if malformed

    # Cellosaurus override
    if evidence["cellosaurus"]["found"]:
        result["label"] = "cell_line"
        result["confidence"] = max(result.get("confidence", 0), 0.95)
        result["reason"] = "Cellosaurus match confirms cell line identity."

    # UniProt fallback
    elif evidence["uniprot"]["found"] and result["label"] == "other":
        result["label"] = "protein"
        result["confidence"] = 0.9

    # PubChem fallback
    elif evidence["pubchem"]["compound"] and result["label"] == "other":
        result["label"] = "drug"
        result["confidence"] = 0.85

    return result