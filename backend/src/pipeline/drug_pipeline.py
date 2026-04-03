
from backend.src.extraction.fields.extract_class import extract_class_info, falsify_class_info
from backend.src.extraction.fields.extract_formula import extract_structural_formula
from backend.src.extraction.fields.extract_active_ingredients import extract_active

def run_drug_pipeline(primary_drug, result, sections):
    
    classified_entities = result.get("classified_entities", [])


    # PHARMACOLOGICAL CLASS EXTRACTION
    pharmacological_class = extract_class_info(primary_drug, sections['abstract'])
    
    falsification_result = falsify_class_info(primary_drug, pharmacological_class.get("class"), pharmacological_class.get("modality"), sections['results'])
    

    # STRUCTURAL FORMULA EXTRACTION

    for entity_info in classified_entities:
        if entity_info.get("entity") == primary_drug:
            
           pubchem_info = entity_info.get("evidence", {}).get("pubchem", {})

    formula = extract_structural_formula(primary_drug, pharmacological_class.get("modality"), pubchem_info)


    # ACTIVE INGREDIENT EXTRACTION

    active_ingrediients = extract_active(primary_drug, result.get("drug_candidates", []), sections['results'])

    return {
        "pharmacological_class": pharmacological_class,
        "falsification": falsification_result,
        "structural_formula": formula,
        "active_ingredients": active_ingrediients
        }
