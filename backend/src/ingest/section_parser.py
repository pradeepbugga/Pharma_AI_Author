
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
        "abstract": abstract_section,
        "results": results_section,
        "discussion": discussion_section,
        "materials_methods": materials_methods_section 
            }

if __name__ == "__main__":
    import json

    with open("./backend/src/data/papers/PMID_36216931/raw_text.json") as f:
        data = json.load(f)

    sections = parse_sections(data)

    print(len(sections["abstract"]))
    print(len(sections["results"]))
    print(len(sections["discussion"]))
    print(len(sections["materials_methods"]))