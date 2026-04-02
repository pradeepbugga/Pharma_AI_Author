
# this script is responsible for normalizing the raw evidence gathered 
# from various sources into a consistent format for the classification step.

def normalize_evidence(raw):
    return {
        "pubchem": {
            "compound": raw.get("pubchem", {}).get("found", False),
            #"substance": raw.get("pubchem_substance", {}).get("found", False),
            "cid": raw.get("pubchem", {}).get("pubchem_id"),
        },
        "uniprot": {
            "found": raw.get("uniprot", {}).get("found", False),
            "id": raw.get("uniprot", {}).get("uniprot_id"),
        },
        "cellosaurus": {
            "found": raw.get("cellosaurus", {}).get("found", False),
            "cvcl": raw.get("cellosaurus", {}).get("cvcl"),
            "atcc": raw.get("cellosaurus", {}).get("atcc_id")
        },
        "web": {
            "used": "web" in raw,
            "top_hits": [
                {
                    "title": r.get("title"),
                    "url": r.get("url")
                }
                for r in raw.get("web", {}).get("results", [])[:2]
            ]
        }
    }
