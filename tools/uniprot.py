import requests

def normalize(s:str):

    return s.replace("-", " ").replace(" ", "").upper()

def lookup_protein(entity:str, session=None) -> dict:
    
    url = "https://rest.uniprot.org/uniprotkb/search"

    if session is None:
        session = requests.Session()

    query = f"gene_exact:{entity} OR protein_name:\"{entity}\" AND reviewed:true AND organism_id:9606"

    params = {
        "query": query, 
        "format": "json", 
        "size": 5}
    try:
        res = session.get(url, params=params, timeout=5)
        res.raise_for_status()
        data = res.json()

        if not data.get("results"):
            return {
                "found": False
            }

        entity_norm = normalize(entity)

        for entry in data["results"]:
            all_names = []

            # Gene names
            for gene in entry.get("genes", []):
                if gene.get("geneName"):
                    all_names.append(gene["geneName"]["value"])
                for syn in gene.get("synonyms", []):
                    all_names.append(syn["value"])

            # Protein names
            desc = entry.get("proteinDescription", {})

            rec = desc.get("recommendedName", {})
            if rec.get("fullName"):
                all_names.append(rec["fullName"]["value"])

            for alt in desc.get("alternativeNames", []):
                if alt.get("fullName"):
                    all_names.append(alt["fullName"]["value"])

            # Normalize + compare
            for entity in all_entity:
                if normalize(entity) == entity_norm:
                    return {
                        "found": True,
                        "type": "protein",
                        "uniprot_id": entry.get("primaryAccession"),
                        "matched_name": entity,
                        "source": "uniprot_reviewed_human"
                    }

    # fallback: weak match if API returned something but no exact match
        return {
            "found": True,
            "type": "protein_candidate",
            "uniprot_id": data["results"][0].get("primaryAccession"),
            "matched_name": None,
            "source": "uniprot_loose"
        }

    except Exception as e:
        return {
            "found": False,
            "error": str(e)
        }
    