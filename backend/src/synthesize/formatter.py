
# this function is designed to parse and format the duration field
# for output in the final structured data. 

def format_duration_field(normalized_output):
        admin_durations = normalized_output.get("administration_duration", [])
        
        if admin_durations:
            # 1. If there are multiple values, we can attempt to create a range 
            values = sorted({
                item['normalized_value']: item for item in admin_durations
            })

            if len(values) == 1:
                main_value = values[0]
            else:
                main_value = f"{values[0]} to {values[-1]}"
            status = "present"
        else:
            main_value = "Not specified"
            status = "missing"

        # 2. Combine all evidence across all categories for full traceability
        all_evidence = []
        for category, items in normalized_output.items():
            for item in items:
                all_evidence.append(f"[{category}] {item['normalized_value']}: {item['evidence']}")
        
        full_source = " | ".join(all_evidence)

        return {
            "value": main_value,
            "status": status,
            "source": "llm_derived",
            "additional_info": f'Evidence: {full_source}'
        }