import pubchempy as pcp
 
def lookup_compound(entity:str):
    results = pcp.get_compounds(entity, 'name')
        
    if results:
        return {
            "found": True,
            "pubchem_id": results[0].cid,
            "type": "compound"
        }
    return {
        "found": False,
        "pubchem_id": None,
        "type": None
        }

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