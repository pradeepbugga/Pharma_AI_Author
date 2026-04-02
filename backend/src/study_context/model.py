
from backend.src.utils.chunk_and_retrieve import split_into_chunks, retrieve_chunks_simple

# this function builds the context for study model extraction.  It takes in the drug name and the text (from abstract and results) 
# and returns the chunks that are relevant to identifying the study model (in vitro, in vivo, clinical). 

def build_study_model_context(primary_drug, text):

    # for debugging
    # total_chunks = split_into_chunks(text)

    IN_VITRO_KEYWORDS = ["cells", "cell line", "in vitro"]
    IN_VIVO_KEYWORDS = ["mice", "xenograft", "tumor"]
    CLINICAL_KEYWORDS = ["patients", "trial", "phase"]

    in_vitro_chunks = retrieve_chunks_simple(text, IN_VITRO_KEYWORDS, primary_drug)
    in_vivo_chunks  = retrieve_chunks_simple(text, IN_VIVO_KEYWORDS, primary_drug)
    clinical_chunks = retrieve_chunks_simple(text, CLINICAL_KEYWORDS, primary_drug)

    return {
        "in_vitro": in_vitro_chunks,
        "in_vivo": in_vivo_chunks,
        "clinical": clinical_chunks
    }



