


def run_drug_pipeline(primary_drug, result, sections):
    
    classified_entities = result.get("classified_entities", [])


    # PHARMACOLOGICAL CLASS EXTRACTION
    pharmacological_class = extract_class_info(primary_drug, sections['abstract'])
    
    #print("\n=== PHARMACOLOGICAL CLASS OUTPUT ===")
    #print(json.dumps(pharmacological_class, indent=2))

    falsification_result = falsify_class_info(primary_drug, pharmacological_class.get("class"), pharmacological_class.get("modality"), sections['results'])
    
    #print("\n=== FALSIFICATION OUTPUT ===")
    #print(json.dumps(falsification_result, indent=2))


    # STRUCTURAL FORMULA EXTRACTION

    pubchem_info = next(
        (e.get("evidence", {}).get("pubchem", {})
            for e in classified_entities if e["entity"] == primary_drug),
        {}
    )

    formula = extract_structural_formula(primary_drug, pharmacological_class.get("modality"), pubchem_info)


    # ACTIVE INGREDIENT EXTRACTION

    active_ingrediients = extract_active_ingredients(primary_drug, result.get("drug_candidates", []), sections['results'])

    return {
        "class": pharmacological_class,
        "falsification": falsification_result,
        "structural_formula": formula,
        "active_ingredients": active_ingrediients
        }
