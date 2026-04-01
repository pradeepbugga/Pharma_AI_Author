import requests

# normalize entity names 

def normalize(s:str):

    return s.replace("-", " ").replace(" ", "").upper()

# We will cross-check proteins / genes with UniProt database using UniProt REST API.

def lookup_protein(entity:str, session=None) -> dict:
    
    url = "https://rest.uniprot.org/uniprotkb/search"

    if session is None:
        session = requests.Session()

    # we restrict to reviewed entries and those coming from human origin 

    query = f"gene_exact:{entity} OR protein_name:\"{entity}\" AND reviewed:true AND organism_id:9606"

    params = {
        "query": query, 
        "format": "json", 
        "size": 5}

    for attempt in range(3):
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
                for entity in all_names:
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
            if attempt == 2:
                return {
                    "found": False,
                    "error": str(e)
                }
            time.sleep(2 ** attempt)  # exponential backoff
        

if __name__ == "__main__":
    results = lookup_protein("SHP2")
    print(results)