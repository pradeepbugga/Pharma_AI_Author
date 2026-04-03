
import json, os
from tqdm import tqdm
from backend.src.extraction.entity.ner import BiomedicalNER
from backend.src.pipeline.entity_extraction import run_ner_pipeline
from backend.src.pipeline.entity_postprocess import count_entities, to_simple_dict
from backend.src.pipeline.ind_pipeline import run_ind_pipeline


JSON_PATH = "./backend/src/data/papers/PMID_36216931/raw_text.json"
model = BiomedicalNER()

def run_demo_pipeline():
    
    with open(JSON_PATH, "r") as f:
        data = json.load(f)
    
    
    labels = ["drug"]

    entities = run_ner_pipeline(data, model, labels)

    entity_counts = count_entities(entities)
    output = to_simple_dict(entity_counts)

    print(type(output))

    results = run_ind_pipeline(output, JSON_PATH)

    return {
        "fields": results["fields"],
        "intro": results["ind_intro"]
    }
    

if __name__ == "__main__":
    result = run_demo_pipeline()
    print(json.dumps(result, indent=2))