from backend.src.pipeline.entity_pipeline_stream import run_entity_pipeline_stream
from backend.src.selection.drug_selection import extract_drug_candidates
from backend.src.selection.drug_selection import select_primary_drug
import asyncio
import time


async def run_pipeline_stream(entities, text):
    print("=== PASS 1: ENTITY PROCESSING ===")

    classified_entities = []

    async for event in run_entity_pipeline_stream(entities, text):
        yield event
        await asyncio.sleep(0)  

        if event.get("status") == "Entity pipeline complete":
            classified_entities = event.get("classified_entities", [])


    print("\n=== PASS 2: DRUG SELECTION ===")

    drug_candidates = extract_drug_candidates(classified_entities)
    print("\nDrug candidates:", drug_candidates)

    primary = select_primary_drug(drug_candidates, text)
    print("\nPrimary drug:", primary)

    yield {
        "status": "Primary drug identified",
        "classified_entities": classified_entities,
        "drug_candidates": drug_candidates,
        "primary_drug": primary
    }

