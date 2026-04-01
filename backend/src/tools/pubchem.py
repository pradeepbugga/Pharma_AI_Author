import pubchempy as pcp
import requests


# We can use pubchempy to speak to PubChem REST API to cross-check compounds

def lookup_compound(entity:str):
    results = pcp.get_compounds(entity, 'name')


    # CID is the PubChem identifier (compound ID)

    if results:
        cid = results[0].cid
        description = get_pubchem_description(cid)
        return {
            "found": True,
            "pubchem_id": cid,
            "description": description,
            "type": "compound"
        }
    return {
        "found": False,
        "pubchem_id": None,
        "type": None
        }

# We can also look up substances (broader category than compounds)

def lookup_substance(entity:str):
    results = pcp.get_substances(entity, 'name')
        
    if results:
        return
        {
            "found": True,
            "pubchem_id": results[0].cid,
            "type": "substance"
        }
    return {
        "found": False,
        "pubchem_id": None,
        "type": None
        }

# Below functions to get the descriptions associated with PubChem entries

def extract_all_descriptions(pug_view_json):
    descriptions = []
    
    # Navigate to Names and Identifiers -> Record Description
    sections = pug_view_json.get('Record', {}).get('Section', [])
    for sec in sections:
        if sec.get('TOCHeading') == 'Names and Identifiers':
            for sub in sec.get('Section', []):
                if sub.get('TOCHeading') == 'Record Description':
                    for info in sub.get('Information', []):
                        # Get the actual text string
                        text = info.get('Value', {}).get('StringWithMarkup', [{}])[0].get('String')
                        if text:
                            descriptions.append(text)
                            
    return " ".join(descriptions)



def get_pubchem_description(cid):
    if not cid:
        return None
    
    
    # PUG-View API endpoint for annotations
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        
        description = extract_all_descriptions(data)    
        return description if description else "No description available."       
                
    except Exception as e:
        print(f"Error fetching description for CID {cid}: {e}")
        
    return "No description available."




if __name__ == "__main__":
    cid = lookup_compound("Aspirin")
    description = get_pubchem_description(cid["pubchem_id"])
    print(f"CID: {cid['pubchem_id']}, Description: {description}")