
import json, os
from tqdm import tqdm
import asyncio
from backend.src.extraction.entity.ner import BiomedicalNER
from backend.src.pipeline.entity_extraction import run_ner_pipeline
from backend.src.pipeline.entity_postprocess import count_entities, to_simple_dict
from backend.src.pipeline.ind_pipeline_stream import run_ind_pipeline_stream


JSON_PATH = "./backend/src/data/papers/PMID_36216931/raw_text.json"
model = BiomedicalNER()

async def run_demo_pipeline_stream():
    
    with open(JSON_PATH, "r") as f:
        data = json.load(f)
    
    
    labels = ["drug"]

    yield {"status": "Running entity extraction"}
    await asyncio.sleep(0)  

    entities = await asyncio.to_thread(run_ner_pipeline, data, model, labels)


    entity_counts = count_entities(entities)
    output = to_simple_dict(entity_counts)

    with open("./extracted_entities2.json", "w") as f:
        json.dump(output, f, indent=2)

    print(type(output))

    yield {"status": "Running IND pipeline"}
    await asyncio.sleep(0)  

    results = None

    async for event in run_ind_pipeline_stream(output, JSON_PATH):
        yield event
        await asyncio.sleep(0)  

        if event.get("status") == "IND pipeline complete":
            results = event

    if results is None:
        raise ValueError("IND pipeline did not complete successfully.")
        

    yield{
        "status": "Done",
        "fields": results["fields"],
        "intro": results["ind_intro"]
    }
    

