

def build_ind_fields(ind_context):
    
    # build final output
    fields = {}

    fields["Drug Name"] = {
        "value": ind_context["drug_name"],
        "status": assign_status(ind_context["drug_name"]),
        "source": "text_extraction"
    }

    fields["Pharmacological Class"] = {
        "value": ind_context["pharmacological_class"].get("class"),
        "status": "present",
        "source": "llm derived"
    }

    fields["Structural Formula"] = {
        "value": ind_context["structural_formula"].get("value").get("molecular_formula") if ind_context["structural_formula"].get("value") else None,
        "status": "present" if ind_context["structural_formula"].get("value").get("molecular_formula") else "missing",
        "source": "pubchem"
    }

    fields["Active Ingredients"] = {
        "value": ind_context["active_ingredients"].get("active_ingredients"),
        "status": assign_status(ind_context["active_ingredients"].get("active_ingredients")),
        "source": "llm derived"
    }   



    fields["Formulation"] = {
        "value": ind_context["formulation"].get("formulation_description"),
        "status": ind_context["formulation"].get("status"),
        "source": ind_context["formulation"].get("evidence", "")
    }   

    # Assuming 'dose' is the dictionary from your "DOSE OUTPUT"
    dose_output = ind_context["dose"]

    # Extract unit safely (e.g., "mg/kg" from "3 mg/kg")
    unit = dose_output["dose_values"][0].split()[-1] if dose_output["dose_values"] else ""

    # Map to your fields object
    fields["Dose"] = {
        # Use the pre-formatted range if it exists, otherwise join the list
        "value": f"{dose_output.get('range', 'N/A')} ({dose_output.get('frequency', '')})",
        "status": "present" if dose_output.get("valid") else "absent",
        "source": f"Route: {dose_output.get('route', {}).get('standard')} | Evidence: {dose_output.get('evidence', '')}"
    }

    fields["Route of Administration"] = {
        "value": ind_context["dose"].get("route"),  
        "status": "present",
        "source": ind_context["dose"].get("evidence", "")
    }

    def format_duration_field(normalized_output):
        # 1. Prioritize the main treatment duration (usually the longest or highest confidence)
        admin_durations = normalized_output.get("administration_duration", [])
        
        if admin_durations:
            # Sort by confidence or length (e.g., picking 28 days over 7 days)
            primary = max(admin_durations, key=lambda x: x['confidence'])
            main_value = primary['normalized_value']
        else:
            main_value = "Not specified"

        # 2. Combine all evidence across all categories for full traceability
        all_evidence = []
        for category, items in normalized_output.items():
            for item in items:
                all_evidence.append(f"[{category}] {item['normalized_value']}: {item['evidence']}")
        
        full_source = " | ".join(all_evidence)

        return {
            "value": main_value,
            "status": "present" if admin_durations else "absent",
            "source": full_source
        }

    fields["Duration"] = format_duration_field(normalized_duration_results)

    fields["Broad Objectives"] = {
        "value": ind_context["objectives"].get("objective"),
        "status": "present",
        "source": "llm_summary"
    }
