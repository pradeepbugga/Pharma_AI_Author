import requests
import re

# this script is for filtering entities that look like cell lines 
# and cross checking against Cellosaurus API


# normalize entity name by removing non-alphanumeric characters and uppercasing
def normalize_name(name):
    return re.sub(r'[^a-zA-Z0-9]', '', name).upper()

# extract ATCC ID from Cellosaurus match - ATCC is also authoritative for cell line identity

def extract_atcc(match):
    
    # from analyzing Cellosaurus JSON results, I found that ATCC IDs are often listed in the "xref-list" section of the response
    
    for ref in match.get("xref-list", []):
        if ref.get("database") == "ATCC":
            return {
                "accession": ref.get("accession"),
                "label": ref.get("label")
            }
    return None

def lookup_cell_line(entity_name: str, session = None) -> dict:
    url = "https://api.cellosaurus.org/search/cell-line"

    if session is None:
        session = requests.Session()

    params = {
        "q": entity_name,
        "format": "json"
    }

    #print("QUERY:", entity_name)  # debug print

    # simple retry

    for attempt in range(3):

        try:
            response = session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Cellosaurus returns a list of matches under "cell-line-list"

            results = data.get("Cellosaurus", {}).get("cell-line-list", [])
        

            if not results:
                return {"found": False}

            entity_norm = normalize_name(entity_name)

            best_match = None

            # we are looking through top 10 results (this should be enough)

            for match in results[:10]:
                names = []

                # find all locations of names in JSON

                # main names
                for n in match.get("name-list", []):
                    names.append(n.get("value", ""))

                # child names
                for c in match.get("child-list", []):
                    if c.get("name"):
                        names.append(c["name"]["value"])

                # accessions
                for acc in match.get("accession-list", []):
                    names.append(acc.get("value", ""))

                # derived

                for parent in match.get("derived-from", []):
                    names.append(parent.get("label", ""))
                    names.append(parent.get("accession", ""))

                # normalize and compare
                for n in names:
                    if normalize_name(n) == entity_norm:
                        best_match = match
                        break

                if best_match:
                    break

        
            if not best_match:
                return {
                    "found": False,
                    "type": "cell_line",
                    "cvcl": None,
                    "atcc_id": None,
                    "canonical_name": None,
                    "source": "cellosaurus"
                }

            #Cellosaurus JSON shows the parent cell line if an unnormalized query is entered

            # PRIORITIZE parent if exists
            parent = best_match.get("derived-from", [])


            if parent:
                cvcl_id = parent[0].get("accession")
                canonical_name = parent[0].get("label")

                # we will use the Cellosaurus CVCL ID as the main identifier for cell lines

                canonical_data = lookup_cell_line_by_cvcl(cvcl_id, session)

                canonical_results = canonical_data.get("Cellosaurus", {}).get("cell-line-list", []) if canonical_data else []

                if canonical_results:
                    match = next(
                        (m for m in canonical_results if m.get("accession-list", [{}])[0].get("value") == cvcl_id),
                        canonical_results[0]
                    )
                    atcc_entry = extract_atcc(match)
                else:
                    atcc_entry = None

            else:
                cvcl_list = best_match.get("accession-list", [])
                cvcl_id = cvcl_list[0].get("value") if cvcl_list else None
                canonical_name = entity_name
                atcc_entry = extract_atcc(best_match)     

            return {
                "found": cvcl_id is not None,
                "type": "cell_line",
                "cvcl": cvcl_id,
                "cellosaurus_url": f"https://www.cellosaurus.org/{cvcl_id}" if cvcl_id else None,
                "atcc_id": atcc_entry.get("accession") if atcc_entry else None,
                "canonical_name": canonical_name,
                "source": "cellosaurus"
            }

        except Exception as e:
            if attempt == 2:
                return {
                    "found": False,
                    "error": str(e)
                }
            time.sleep(2 ** attempt)  # exponential backoff

# this function looks up cell line by CVCL ID (unlike above which uses free text search)

def lookup_cell_line_by_cvcl(cvcl_id, session=None):
    if session is None:
        session = requests.Session()

    url = f"https://api.cellosaurus.org/cell-line/{cvcl_id}"

    for attempt in range(3):
        try:
            resp = session.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            if attempt == 2:
                return None
            time.sleep(2 ** attempt)  # exponential backoff

# cell lines can have different forms so we will try to handle those 

def generate_surface_forms(entity):
    forms = set()

    forms.add(entity)
    forms.add(entity.replace("-", ""))
    forms.add(entity.replace(" ", ""))

    # A549 → A-549
    forms.add(re.sub(r'([A-Za-z])(\d)', r'\1-\2', entity))

    # A549 → A 549
    forms.add(re.sub(r'([A-Za-z])(\d)', r'\1 \2', entity))

    return forms

# can use this to filter entities that look like cell lines before calling Cellosaurus API to save time and avoid false positives

def looks_like_cell_line(entity):
    return any(c.isdigit() for c in entity) and len(entity) <= 10


if __name__ == "__main__":

    print(normalize_name("SNU-1033"))  # debug print
    results = lookup_cell_line("SNU-1033")
    print(results)