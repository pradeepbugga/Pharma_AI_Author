
def parse_sections(data):
    abstract_section = []
    results_section = []
    discussion_section = []
    materials_methods_section = []

    for section in data.get("sections", []):
        
        if section.get("major_heading", "") == "Abstract":
            
            abstract_section.append(section.get("section_text", ""))
        elif section.get("major_heading", "") == "Results":
            
            results_section.append(section.get("section_text", ""))
        elif section.get("major_heading", "") == "Discussion":      
            discussion_section.append(section.get("section_text", ""))
        elif section.get("major_heading", "") == "Materials and Methods":
            
            materials_methods_section.append(section.get("section_text", ""))

    return {
        "abstract": " ".join(abstract_section),
        "results": " ".join(results_section),
        "discussion": " ".join(discussion_section),
        "materials_methods": " ".join(materials_methods_section)
    }