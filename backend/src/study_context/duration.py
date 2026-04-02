
from backend.src.utils.chunk_and_retrieve import split_into_chunks, retrieve_chunks_simple

# this function 

def build_duration_context(sections):

    text = sections['abstract'] + "" + sections['results']
    duration_candidates = extract_duration_candidates(text)
    duration_contexts = get_duration_contexts(text, duration_candidates)

    return {
        "duration_candidates": duration_candidates,
        "duration_contexts": duration_contexts
    }