
# this function is designed to parse and format the duration field
# for output in the final structured data. 

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
            "source": "llm_derived",
            "additional_info": f'Evidence: {full_source}'
        }