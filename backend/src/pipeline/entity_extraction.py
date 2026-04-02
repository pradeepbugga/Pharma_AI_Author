from backend.src.ingest.section_filter import filter_sections
from backend.src.utils.text_cleaning import clean_biomedical_text

def run_ner_pipeline(data,ner_model, labels):
    # this function runs the NER pipeline on the filtered sections of the paper. 
    # it takes in the raw data, the NER model, and the list of labels to extract.
    # it returns a list of identified entities with their labels and the text evidence.
    
    entities = []

    filtered_sections = filter_sections(data)

    for section in filtered_sections:
        text = section['section_text']

        cleaned_text = clean_biomedical_text(text)

        # if text has multiple paragraphs, split them and predict entities for each paragraph
        text_sections = cleaned_text.split("\n\n")

        for text_section in text_sections:
            section_entities = ner_model.extract(text_section, labels)
            entities.extend(section_entities)
    
    return entities