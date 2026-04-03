import re

# this function is designed to parse and format the duration field
# for output in the final structured data. 

def format_duration_field(normalized_output):
    
    admin_durations = normalized_output.get("administration_duration", [])
    
    if not admin_durations:
        main_value = "Not specified"
        status = "missing"
    else:
        # Get unique normalized values (e.g., ["7 days", "28 days"])
        unique_values = list({item['normalized_value'] for item in admin_durations})

        # CRITICAL FIX: Numeric Sort (so 7 comes before 28)
        def get_days(s):
            match = re.search(r"(\d+)", s)
            return int(match.group(1)) if match else 0
        
        sorted_values = sorted(unique_values, key=get_days)

        if len(sorted_values) == 1:
            main_value = sorted_values[0]
        else:
            main_value = f"{sorted_values[0]} to {sorted_values[-1]}"
        status = "present"

    # 2. Structured Evidence Mapping
    # Instead of one giant string, let's group evidence by its actual classification
    evidence_by_type = {}
    for category, items in normalized_output.items():
        # Keep only unique evidence per category to reduce "giant text"
        snippets = []
        for item in items:
            snippets.append(f"{item['normalized_value']}: {item['evidence']}")
        
        if snippets:
            evidence_by_type[category] = " | ".join(snippets)

    return {
        "value": main_value,
        "status": status,
        "source": "llm_derived",
        "additional_info": {
            "primary_evidence": evidence_by_type.get("administration_duration", "No admin duration found"),
            "contextual_info": {k: v for k, v in evidence_by_type.items() if k != "administration_duration"}
        }
    }