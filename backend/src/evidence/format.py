
# this function is used to format the evidence in a consistent way
#  to be attached to the classification result for each entity
def compute_evidence_used(evidence):
    return {
        "pubchem": evidence["pubchem"]["compound"],
        "uniprot": evidence["uniprot"]["found"],
        "cellosaurus": evidence["cellosaurus"]["found"],
        "web": evidence["web"]["used"]
    }