import pubchempy as pcp


# this function extracts structural formula using PubChemPy
# we will get the molecular formula, SMILES, and InChI if CID is available.

def extract_structural_formula(drug, modality, pubchem_info):
    if modality != "small_molecule":
        return {
            "value": {

            "molecular_formula": None,
            "smiles": None,
            "inchi": None},  
            "status": "not_applicable"

        }


    if pubchem_info.get("compound") and pubchem_info.get("cid"):

        try:
            # Fetch compound info from PubChem
            cid = pubchem_info["cid"]
            pubchem_data = pcp.Compound.from_cid(cid).to_dict()
        
            return {
                "value": {
                "molecular_formula": pubchem_data["molecular_formula"],
                "smiles": pubchem_data["smiles"],
                "inchi": pubchem_data["inchi"]},
                "status": "present",
                "source": "pubchem"
            }
        except Exception as e:
            pass

    return {
        "value": {
        "molecular_formula": None,
        "smiles": None,
        "inchi": None},
        "status": "missing"
    }