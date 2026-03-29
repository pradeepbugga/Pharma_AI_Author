from tools.pubchem import lookup_compound
from tools.uniprot import lookup_protein
from tools.cellosaurus import lookup_cell_line
from tools.web_search import lookup_web_search


def gather_evidence(entity, session):
    evidence = {}

    evidence["pubchem"] = lookup_compound(entity)
    evidence["uniprot"] = lookup_protein(entity, session)
    evidence["cellosaurus"] = lookup_cell_line(entity, session)

    # web fallback
    if not evidence["pubchem"]["found"] and not evidence["uniprot"]["found"]:
        evidence["web"] = lookup_web_search(entity)

    return evidence