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
        "source": "llm derived",
        "confidence": ind_context["drug_name"].get("confidence", "N/A"),
        "evidence": ind_context["drug_name"].get("evidence", "N/A")
    }

    # ----- PHARMACOLOGICAL CLASS -----

    fields["Pharmacological Class"] = {
        "value": ind_context["pharmacological_class"].get("class"),
        "status": "present" if ind_context["pharmacological_class"].get("class") else "missing",
        "source": "llm derived",
        "confidence": ind_context["pharmacological_class"].get("confidence", "N/A"),
        "evidence": ind_context["falsification"].get("mechanism_evidence", "N/A")
        }

    # ----- STRUCTURAL FORMULA ------

    struct_formula_result = ind_context.get("structural_formula", {})
    inner_values = struct_formula_result.get("value", {})

    fields["Structural Formula"] = {
        "value": inner_values.get("molecular_formula"),
        "status": struct_formula_result.get("status", "missing"),
        "source": struct_formula_result.get("source", "missing"),
        "confidence": struct_formula_result.get("confidence", "N/A"),
        "evidence": struct_formula_result.get("evidence", "N/A")    
    }

    # ----- ACTIVE INGREDIENTS -----

    fields["Active Ingredients"] = {
        "value": ind_context.get("active_ingredients",{}).get("active_ingredients"),
        "status": assign_status(ind_context.get("active_ingredients",{}).get("active_ingredients")),
        "source": "llm derived",
        "confidence" : ind_context.get("active_ingredients",{}).get("confidence", "N/A"),
        "evidence": ind_context.get("active_ingredients",{}).get("evidence", "N/A")
    }   

    # ----- FORMULATION -----

    fields["Formulation"] = {
        "value": ind_context.get("formulation", {}).get("formulation_description"),
        "status": assign_status(ind_context.get("formulation", {}).get("formulation_description")),
        "source": "llm derived",
        "evidence": ind_context.get("formulation", {}).get("evidence", "N/A"),
        "confidence": ind_context.get("formulation", {}).get("confidence", "N/A")
        }


    # ----- DOSE ------

    dose_output = ind_context.get("dose", {})

    # display dose value
    display_value = dose_output.get("range")

    if not display_value:
        display_value = "N/A"

    frequency = dose_output.get("frequency", "")
    if frequency:
        value = f"{display_value} ({frequency})"
    else:
        value = display_value

    fields["Dose"] = {
        
        "value": value,
        "status": "present" if dose_output.get("valid") else "missing",
        "source": "llm derived",
        "confidence": dose_output.get("confidence", "N/A"),
        "evidence": dose_output.get("evidence", "N/A")}


    # ----- ROUTE OF ADMINISTRATION -----

    fields["Route of Administration"] = {
        "value": ind_context.get("dose", {}).get("route"),
        "status": "present" if ind_context.get("dose", {}).get("route") else "missing",
        "source": "llm derived",
        "confidence": ind_context.get("dose", {}).get("confidence", "N/A"),
        "evidence": ind_context.get("dose", {}).get("evidence", "N/A")}

    # ----- DURATION -----

    formatted_duration = format_duration_field(ind_context.get("duration", {}))

    fields["Duration"] = formatted_duration

    fields["Broad Objectives"] = {
        "value": ind_context["broad_objectives"].get("objective"),
        "status": "present" if ind_context["broad_objectives"].get("objective") else "missing",
        "source": "llm_derived"
    }

    return fields