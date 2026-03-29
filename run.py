import json
from pipeline.main import run_pipeline

# Example: plug in your GLiNER output
entities = [
    "DMSO",
    "SHP2",
    "MRTX1133",
    "KRAS",
    "A549"
]

# Load manuscript text (your JSON file)
with open("./data/papers/PMID_36216931/raw_text.json") as f:
    data = json.load(f)

# Combine relevant sections
text = " ".join(
    s["section_text"]
    for s in data["sections"]
    if s["major_heading"] in ["Abstract", "Results"]
)

result = run_pipeline(entities, text)

print("\n=== FINAL OUTPUT ===")
print(json.dumps(result, indent=2))