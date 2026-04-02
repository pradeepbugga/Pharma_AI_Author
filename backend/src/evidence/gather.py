from backend.src.tools.pubchem import lookup_compound
from backend.src.tools.uniprot import lookup_protein
from backend.src.tools.cellosaurus import lookup_cell_line, generate_surface_forms
from backend.src.tools.web_search import lookup_web_search

#this script is responsible for gathering evidence for a given entity from various sources
# (PubChem, UniProt, Cellosaurus, web search) to be used in the classification step.

def gather_evidence(entity, session):
    evidence = {}

    # Initial database lookups

    evidence["pubchem"] = lookup_compound(entity)

    evidence["uniprot"] = lookup_protein(entity, session)

    evidence["cellosaurus"] = lookup_cell_line(entity, session)


    # Heuristic: if no evidence found, try synonyms for cell lines (common issue)
    if not evidence["cellosaurus"]["found"]:d
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