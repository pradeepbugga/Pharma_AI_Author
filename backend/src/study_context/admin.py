
from backend.src.utils.chunk_and_retrieve import split_into_chunks, retrieve_chunks_simple

# this function builds the context for administration extraction.  It takes in the drug name, the identified study model, 
# the chunks that were identified as relevant to study model classification, and the text.

def build_administration_context(primary_drug, sections, study_model, model_context):

    ADMIN_KEYWORDS = ["administered", "treatment", "treated with", "dosed", "given", "received", "mg/kg"]

    admin_chunks = retrieve_chunks_simple(" ".join(sections['abstract'] + sections['results']), 
    ADMIN_KEYWORDS, primary_drug)

    model_chunks = []
    # these are chunks that are relevant to the study model classification - we will use them as additional context for administration detection    model_chunks = []
    for component in study_model.get("components", []):
        model_chunks.extend(model_context.get(component, []))

    # Deduplicate by using the 'text' field as a unique key
    def dedup(chunks):
        return list({c["text"]: c for c in chunks}.values())

    return {
        "admin_chunks": dedup(admin_chunks),
        "model_chunks": dedup(model_chunks)
    }