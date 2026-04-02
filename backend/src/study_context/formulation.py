
from backend.src.utils.chunk_and_retrieve import retrieve_chunks_simple

# this function builds the context for formulation extraction. 
# It uses keyword filtering to find chunks that are relevant to formulation
# then the extraction function will look for specific formulation information within those chunks.

def build_formulation_context(primary_drug, sections):

    FORMULATION_KEYWORDS = [
        "formulated in",
        "vehicle",
        "dissolved in",
        "prepared in",
        "resuspended in",
        "diluted in"
    ]

    text = sections['abstract'] + "" + sections['results'] + "" + sections['materials_methods']

    formulation_chunks = retrieve_chunks_simple(text, FORMULATION_KEYWORDS, primary_drug)

    return formulation_chunks
