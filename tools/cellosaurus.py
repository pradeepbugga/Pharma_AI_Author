import requests
import re

def normalize_name(name):
    return re.sub(r'[^a-zA-Z0-9]', '', name).lower()

def extract_atcc(match):
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

    try:
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = data.get("Cellosaurus", {}).get("cell-line-list", [])
      

        if not results:
            return {"found": False}

        entity_norm = normalize_name(entity_name)

        best_match = None

        for match in results[:10]:
            names = []

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

        # fallback: take first result if no exact match
        if not best_match:
            best_match = results[0]
            match_type = "loose"
        else:
            match_type = "exact"

        # PRIORITIZE parent if exists
        parent = best_match.get("derived-from", [])

        if parent:
            cvcl_id = parent[0].get("accession")
            canonical_name = parent[0].get("label")

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
        return {
            "found": False,
            "error": str(e)
        }

def lookup_cell_line_by_cvcl(cvcl_id, session=None):
    if session is None:
        session = requests.Session()

    url = f"https://api.cellosaurus.org/cell-line/{cvcl_id}"

    try:
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None

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

def looks_like_cell_line(entity):
    return any(c.isdigit() for c in entity) and len(entity) <= 10


if __name__ == "__main__":
    results = lookup_cell_line("KRAS-WT")
    print(results)