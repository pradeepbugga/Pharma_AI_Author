def extract_drug_candidates(classified_entities):
    return [
        e["entity"]
        for e in classified_entities
        if e["label"] == "drug"
    ]