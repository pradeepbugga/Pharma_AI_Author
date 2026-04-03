from backend.src.synthesize.formatter import format_duration_field

def build_ind_fields(ind_context):
    

    def assign_status(value):
        if value is None:
            return "missing"
        if value == "not_applicable":
            return "not_applicable"
        return "present"


    # build final output
    fields = {}

    # ----- DRUG NAME -----

    fields["Drug Name"] = {
        "value": ind_context["drug_name"]["primary_drug"],
        "status": "present" if ind_context["drug_name"]["primary_drug"] else "missing",
        "source": "llm derived"
        "additional_info": f'Confidence: {ind_context["drug_name"]['confidence']}'
    }

    # ----- PHARMACOLOGICAL CLASS -----

    fields["Pharmacological Class"] = {
        "value": ind_context["pharmacological_class"].get("class"),
        "status": "present" if ind_context["pharmacological_class"].get("class") else "missing",
        "source": "llm derived",
        "additional_info": f'Modality: {ind_context["pharmacological_class"].get("modality", "N/A")} | Evidence: {ind_context["falsification"].get("mechanism_evidence", "N/A")}'
    }

    # ----- STRUCTURAL FORMULA ------

    struct_formula_result = ind_context.get("structural_formula", {})
    inner_values = struct_formula_result.get("value", {})

    fields["Structural Formula"] = {
        "value": inner_values.get("molecular_formula"),
        "status": struct_formula_result.get("status", "missing"),
        "source": struct_formula_result.get("source", "missing")
    }

    # ----- ACTIVE INGREDIENTS -----

    fields["Active Ingredients"] = {
        "value": ind_context.get("active_ingredients",{}).get("active_ingredients"),
        "status": assign_status(ind_context.get("active_ingredients",{}).get("active_ingredients")),
        "source": "llm derived",
        "additional_info": f'Confidence: {ind_context.get("active_ingredients",{}).get("confidence", "N/A")}'
    }   

    # ----- FORMULATION -----

    fields["Formulation"] = {
        "value": ind_context.get("formulation", {}).get("formulation_description"),
        "status": assign_status(ind_context.get("formulation", {}).get("formulation_description")),
        "source": "llm derived",
        "additional_info": f'Evidence: {ind_context.get("formulation", {}).get("evidence", "N/A")} | Confidence: {ind_context.get("formulation", {}).get("confidence", "N/A")}'
        }


    # ----- DOSE ------

    dose_output = ind_context.get("dose", {})

    # display dose value
    if dose_output.get("dose_type") == "range" and dose_output.get("range"):
        display_value = dose_output["range"]
    elif dose_output.get("dose_values"):
        # join if list
        display_value = ", ".join(map(str, dose_output["dose_values"]))
    else:
        display_value = "N/A"


    fields["Dose"] = {
        
        "value": f"{display_value} ({dose_output.get('frequency', 'N/A')})",
        "status": "present" if dose_output.get("valid") else "missing",
        "source": "llm derived",
        "additional_info": f"Evidence: {dose_output.get('evidence', '')} | Confidence: {dose_output.get('confidence', 'N/A')} 
        }


    # ----- ROUTE OF ADMINISTRATION -----

    fields["Route of Administration"] = {
        "value": ind_context.get("dose", {}).get("route"),
        "status": "present" if ind_context.get("dose", {}).get("route") else "missing",
        "source": "llm derived",
        "additional_info": f"Evidence: {ind_context.get('dose', {}).get('evidence', '')} | Confidence: {ind_context.get('dose', {}).get('confidence', 'N/A')}"
    }

    # ----- DURATION -----

    formatted_duration = format_duration_field(ind_context.get("duration", {}))

    fields["Duration"] = formatted_duration

    fields["Broad Objectives"] = {
        "value": ind_context["objectives"].get("objective"),
        "status": "present",
        "source": "llm_summary"
    }
