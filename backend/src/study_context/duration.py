
from backend.src.extraction.fields.extract_duration import extract_duration_candidates, get_duration_contexts

# this function builds the context for duration extraction. It uses keyword filtering 
# similar to what we do for study model and administration

def build_duration_context(sections):

    text = sections['abstract'] + "" + sections['results']
    duration_candidates = extract_duration_candidates(text)
    duration_contexts = get_duration_contexts(text, duration_candidates)

    return {
        "duration_candidates": duration_candidates,
        "duration_contexts": duration_contexts
    }