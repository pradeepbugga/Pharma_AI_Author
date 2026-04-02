from backend.src.pipeline.entity_processor import process_entity

def run_entity_pipeline(entities, text):
    session = requests.Session()

    classified_entities = []
    seen = set()

    for entity in entities:
        canonical, result = process_entity(entity, text, session)

        if canonical in seen:
            continue
        
        seen.add(canonical)

        classified_entities.append((canonical, result))

        print(f"Processed entity: {canonical}, result: {result}")

    return classified_entities