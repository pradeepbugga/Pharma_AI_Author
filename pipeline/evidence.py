from tools.pubchem import lookup_compound
from tools.uniprot import lookup_protein
from tools.cellosaurus import lookup_cell_line, generate_surface_forms, looks_like_cell_line
from tools.web_search import lookup_web_search


def gather_evidence(entity, session):
    evidence = {}

    # Initial database lookups

    evidence["pubchem"] = lookup_compound(entity)

    evidence["uniprot"] = lookup_protein(entity, session)

    evidence["cellosaurus"] = lookup_cell_line(entity, session)


    # Heuristic: if no evidence found, try synonyms for cell lines (common issue)
    if not evidence["cellosaurus"]["found"] and looks_like_cell_line(entity):
        for form in generate_surface_forms(entity):
            #print(f"Trying cell line synonym: {form}")
            if form != entity:
                retry = lookup_cell_line(form, session)
                if retry["found"]:
                    retry["alias_used"] = form
                    retry["original_query"] = entity
                    evidence["cellosaurus"] = retry
                    break


    # web fallback
    if (
        not evidence["pubchem"]["found"] and
        not evidence["uniprot"]["found"] and
        not evidence["cellosaurus"]["found"]
    ):
        evidence["web"] = lookup_web_search(entity)

    return evidence