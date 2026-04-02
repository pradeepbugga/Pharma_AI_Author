#this function filters data based on section headings

def filter_sections(data, allowed_sections=("Abstract", "Results")):
    return [
        item for item in data["sections"]
        if item["major_heading"] in allowed_sections
    ]