from backend.src.pipeline.entity_processor import process_entity
import requests
import time
import asyncio

async def run_entity_pipeline_stream(entities, text):
    session = requests.Session()

    classified_entities = []
    seen = set()

    for entity in entities:
        canonical, result = process_entity(entity, text, session)

        if canonical in seen:
            continue
        
        seen.add(canonical)

        classified_entities.append(result)

        yield { "status": f"Processed entity {entity}" }
        await asyncio.sleep(0)
 
        print(f"Processed entity: {canonical}, result: {result}")

    yield {
        "status": "Entity pipeline complete",
        "classified_entities": classified_entities
    }