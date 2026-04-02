# this script postprocesses NER output to count 
# entities then output a simple dictionary of entity name and count to a json file.

def count_entities(entities):
    entity_counts = {}

    for entity in entities:
        key = (entity["text"], entity["label"])
        entity_counts[key] = entity_counts.get(key, 0) + 1

    return entity_counts


def to_simple_dict(entity_counts):
    return {entity[0]: count for entity, count in entity_counts.items()}