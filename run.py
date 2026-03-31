import json
from pipeline.main import run_pipeline
from extract_class import extract_class_info, falsify_class_info
from extract_formula import extract_structural_formula
from extract_active_ingredients import extract_active
from detect_study_model import detect_model
from utils.chunk_and_retrieve import retrieve_chunks_simple, split_into_chunks, filter_chunks
from detect_administration import detect_admin
from detect_dose import extract_dose_candidates, split_by_unit, summarize_dose_range, detect_dose_LLM, get_dose_contexts
from detect_duration import extract_duration_candidates, get_duration_contexts, detect_duration_LLM, normalize_durations
from collections import defaultdict
from detect_formulation import detect_formulation
from detect_broad_objectives import detect_objectives

# Example: plug in your GLiNER output
#entities = [
#    "DMSO",
#    "SHP2",
#    "MRTX1133",
#    "KRAS",
#    "A549"
#]

# load json
with open("./extracted_entities.json") as f:
    entity_counts = json.load(f)

entities = list(entity_counts.keys())

# Load manuscript text (your JSON file)
with open("./data/papers/PMID_36216931/raw_text.json") as f:
    data = json.load(f)


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

# Combine relevant sections
text = "".join(abstract_section + results_section)

'''
result = run_pipeline(entities, text)

print("\n=== FINAL OUTPUT ===")
print(json.dumps(result, indent=2))

primary_drug = result.get("primary_drug", "N/A").get("primary_drug", "N/A")
print(f"\nPrimary drug selected: {primary_drug}")

pharmacological_class = extract_class_info(primary_drug, abstract_section)
print("\n=== PHARMACOLOGICAL CLASS OUTPUT ===")
print(json.dumps(pharmacological_class, indent=2))

falsification_result = falsify_class_info(primary_drug, pharmacological_class.get("class"), pharmacological_class.get("modality"), results_section)
print("\n=== FALSIFICATION OUTPUT ===")
print(json.dumps(falsification_result, indent=2))

#------------EXTRACT STRUCTURAL FORMULA -----------------
classified_entities = result.get("classified_entities", [])

#classified_entities = [{'entity': 'MRTX1133', 'label': 'drug', 'confidence': 1.0, 'reason': 'Context describes MRTX1133 as a potent, selective KRAS^G12D inhibitor discovered through structure-based drug design and characterized by sub-nanomolar binding affinity, confirming it is a small-molecule therapeutic agent.', 'evidence': {'pubchem': {'compound': True, 'cid': 156124857}, 'uniprot': {'found': False, 'id': None}, 'cellosaurus': {'found': False, 'cvcl': None, 'atcc': None}, 'web': {'used': False, 'top_hits': []}}, 'evidence_used': {'pubchem': True, 'uniprot': False, 'cellosaurus': False, 'web': False}}]
#primary_drug = "MRTX1133"
for entity_info in classified_entities:
    if entity_info.get("entity") == primary_drug:
        print(f"\nExtracting structural formula for primary drug: {primary_drug}")
        pub_chem_info = entity_info.get("evidence", {}).get("pubchem", {})

extracted_formula = extract_structural_formula(primary_drug, "small_molecule", pub_chem_info)
print("\n=== STRUCTURAL FORMULA OUTPUT ===")
print(json.dumps(extracted_formula, indent=2))

#------------EXTRACT ACTIVE INGREDIENTS -----------------
drug_candidates = result.get("drug_candidates", [])

#drug_candidates = [
#    "MRTX1133",
#    "erlotinib",
#    "cetuximab",
#    "alpelisib",
#    "GDC-0077",
#    "MRTX849",
#    "afatinib",
#    "BYL-719"
#  ]

active_ingredients = extract_active(primary_drug, drug_candidates, results_section)
print("\n=== ACTIVE INGREDIENTS OUTPUT ===")
print(json.dumps(active_ingredients, indent=2))

'''
#------------DETECT STUDY MODEL -----------------
'''
total_chunks = split_into_chunks(text)
print(f"\nTotal chunks created: {len(total_chunks)}")


IN_VITRO_KEYWORDS = ["cells", "cell line", "in vitro"]
IN_VIVO_KEYWORDS = ["mice", "xenograft", "tumor"]
CLINICAL_KEYWORDS = ["patients", "trial", "phase"]

in_vitro_chunks = retrieve_chunks_simple(text, IN_VITRO_KEYWORDS, "MRTX1133")
in_vivo_chunks  = retrieve_chunks_simple(text, IN_VIVO_KEYWORDS, "MRTX1133")
clinical_chunks = retrieve_chunks_simple(text, CLINICAL_KEYWORDS, "MRTX1133")

has_in_vitro = len(in_vitro_chunks) > 0
has_in_vivo  = len(in_vivo_chunks) > 0
has_clinical = len(clinical_chunks) > 0

print("\n=== CHUNKS RETRIEVED FOR STUDY MODEL DETECTION ===")
print(f"In vitro chunks: {len(in_vitro_chunks)}")
print(f"In vivo chunks: {len(in_vivo_chunks)}")
print(f"Clinical chunks: {len(clinical_chunks)}")

study_model = detect_model('MRTX1133', in_vitro_chunks, in_vivo_chunks, clinical_chunks)
print("\n=== STUDY MODEL OUTPUT ===")
print(json.dumps(study_model, indent=2))

chunk_map = {
    "in_vitro": in_vitro_chunks,
    "in_vivo": in_vivo_chunks,
    "clinical": clinical_chunks
}

#------------DETECT ADMINISTRATION -----------------

ADMIN_KEYWORDS = ["administered", "treatment", "treated with", "dosed", "given", "received", "mg/kg"]
admin_chunks = retrieve_chunks_simple(text, ADMIN_KEYWORDS, "MRTX1133")

print(f"\nChunks retrieved for administration detection: {len(admin_chunks)}")

model_chunks = []
for component in study_model.get("components", []):
    model_chunks.extend(chunk_map.get(component, []))

# 2. Deduplicate by using the 'text' field as a unique key
# We use a dictionary comprehension because dict keys are unique by nature
def dedup(chunks):
    return list({c["text"]: c for c in chunks}.values())

explicit_admin_chunks = dedup(admin_chunks)
explicit_model_chunks = dedup(model_chunks)

administration_info = detect_admin('MRTX1133', admin_chunks, model_chunks, study_model)
print("\n=== ADMINISTRATION OUTPUT ===")
print(json.dumps(administration_info, indent=2))

has_human_data = administration_info.get("clinical", {}).get("value", False) 
print(f"\nDoes the study include human data? {'Yes' if has_human_data else 'No'}")

#------------DETECT DOSE------------------
dose_candidates = extract_dose_candidates(text)
deduped_dose_candidates = sorted(set([c.strip().lower() for c in dose_candidates]))
split_dose_candidates = split_by_unit(deduped_dose_candidates)
summarized_dose_range = summarize_dose_range(split_dose_candidates[0]) if split_dose_candidates[0] else None

dose_contexts = get_dose_contexts(text, split_dose_candidates[0])

dose_info = detect_dose_LLM('MRTX1133', split_dose_candidates[0], dose_contexts, admin_chunks, administration_info)

print("\n=== DOSE OUTPUT ===")
print(json.dumps(dose_info, indent=2))


#------------DETECT DURATION------------------

duration_candidates = extract_duration_candidates(text)
print(f"\nDuration candidates extracted: {duration_candidates}")

duration_contexts = get_duration_contexts(text, duration_candidates)

duration_results = []
duration_results_full = []
for d in duration_contexts:
    duration_context = get_duration_contexts(text, d)
    duration_info = detect_duration_LLM('MRTX1133',d, duration_contexts, admin_chunks, administration_info, dose_info)
    duration_results.append((d, duration_info["classification"]))
    duration_results_full.append({
        "value": d,
        "classification": duration_info["classification"],
        "evidence": duration_info.get("evidence", ""),
        "confidence": duration_info.get("confidence", 0)
    })

grouped = defaultdict(list)

for d, classification in duration_results:
    grouped[classification].append(d)

normalized_duration_results = normalize_durations(grouped, duration_results_full)


print("\n=== DURATION OUTPUT ===")
print(json.dumps(normalized_duration_results, indent=2))
'''
#------------DETECT FORMULATION------------------
FORMULATION_KEYWORDS = [
    "formulated in",
    "vehicle",
    "dissolved in",
    "prepared in",
    "resuspended in",
    "diluted in"
]
formulation_chunks = retrieve_chunks_simple(text + " ".join(materials_methods_section), FORMULATION_KEYWORDS, "MRTX1133")
formulation_info = detect_formulation('MRTX1133', formulation_chunks)

print("\n=== FORMULATION OUTPUT ===")
print(json.dumps(formulation_info, indent=2))

#------------BROAD OBJECTIVES ------------------

input_objective_text = abstract_section + discussion_section

broad_objectives = detect_objectives('MRTX1133', input_objective_text)

print("\n=== BROAD OBJECTIVES OUTPUT ===")
print(json.dumps(broad_objectives, indent=2))

