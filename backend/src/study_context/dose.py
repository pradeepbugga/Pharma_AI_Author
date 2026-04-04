from backend.src.extraction.fields.extract_dose import extract_dose_candidates, split_by_unit, summarize_dose_range, get_dose_contexts

# this function builds the context for dose extraction.  It takes in the drug name, the sections of text, 
# the identified study model and the model context, and returns the identified dose candidates, the contexts for those candidates

def build_dose_context(primary_drug, sections):

    text = " ".join(sections['abstract'] + sections['results'])
    # Extract dose candidates from the text
    dose_candidates = extract_dose_candidates(text)

    # Process the dose candidates: deduplicate, split by unit, and summarize dose range    
    deduped_dose_candidates = sorted(set([c.strip().lower() for c in dose_candidates]))

    split_dose_candidates = split_by_unit(deduped_dose_candidates)

    summarized_dose_range = summarize_dose_range(split_dose_candidates[0]) if split_dose_candidates[0] else None

    dose_contexts = get_dose_contexts(text, split_dose_candidates[0])

    return {
        "in_vivo_dose_candidates": split_dose_candidates[0],
        "dose_contexts": dose_contexts
    }

