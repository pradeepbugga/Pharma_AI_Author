import requests
import re

def normalize_name(name):
    return re.sub(r'[^a-zA-Z0-9]', '', name).lower()


def lookup_cell_line(entity_name: str, session = None) -> dict:
    url = "https://api.cellosaurus.org/search/cell-line"

    if session is None:
        session = requests.Session()

    params = {
        "q": entity_name,
        "format": "json"
    }

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

        cvcl_list = best_match.get("accession-list", [])
        cvcl_id = cvcl_list[0].get("value") if cvcl_list else None

        parent_label = find_parent_label(best_match)
        atcc_entry = find_atcc_data(best_match)

        return {
            "found": True,
            "type": "cell_line",
            "match_type": match_type,
            "cvcl_id": cvcl_id,
            "cellosaurus_url": f"https://www.cellosaurus.org/{cvcl_id}" if cvcl_id else None,
            "atcc_id": atcc_entry.get("accession") if atcc_entry else None,
            "canonical_name": parent_label if parent_label else entity_name,
            "source": "cellosaurus"
        }

    except Exception as e:
        return {
            "found": False,
            "error": str(e)
        }