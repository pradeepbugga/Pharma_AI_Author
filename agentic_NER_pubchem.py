from gliner import GLiNER
import json
import torch 
import re
import pubchempy as pcp
from tqdm import tqdm
import requests
import time

# load model from local directory
model = GLiNER.from_pretrained("gliner-biomed-base-v1.0").to("cuda")

JSON_PATH = "./data/papers/PMID_36216931/raw_text.json"

with open(JSON_PATH, "r") as f:
    data = json.load(f)

sections = []

for item in data['sections']:
    if item['major_heading'] in ["Abstract", "Results"]:
        sections.append(item)


# Tell the model EXACTLY what to look for
labels = ["drug"]

# STEP 1 - Greedy approach: predict entities for each section and combine results

entities = []

for section in sections:
    text = section['section_text']

    # if text has multiple paragraphs, split them and predict entities for each paragraph
    text_sections = text.split("\n\n")

    for text_section in text_sections:
        section_entities = model.predict_entities(text_section, labels)
        entities.extend(section_entities)

# print unique entities
unique_entities = {(entity['text'], entity['label']) for entity in entities}

# print unique entities along with their count in the text
entity_counts = {}
for entity in entities:
    key = (entity['text'], entity['label'])
    if key in entity_counts:
        entity_counts[key] += 1
    else:
        entity_counts[key] = 1

#for entity, count in entity_counts.items():
#    print(f"{entity[0]} ({entity[1]}): {count}")


# STEP 2 - Agentic Reasoning 
# use PubChemPy, Cellosaurus, and UniProt to verify if the extracted entities are indeed drugs or not.

validated_drugs = {}

def find_atcc_data(obj):
    # If we found a dictionary, check if it's the one we want
    if isinstance(obj, dict):
        

        if obj.get("database") == "ATCC":
            
            return obj
        # Otherwise, search all values in this dictionary
        for value in obj.values():
            
            result = find_atcc_data(value)
            if result: return result
            
    # If we found a list, search every item in the list
    elif isinstance(obj, list):
        
        for item in obj:
            result = find_atcc_data(item)
            if result: return result
            
    return None


def find_parent_label(data):
    """
    Recursively searches for the 'derived-from' key and returns 
    the 'label' of the first parent found.
    """
    if isinstance(data, dict):
        # Check if this dictionary contains the 'derived-from' list
        if "derived-from" in data and isinstance(data["derived-from"], list):
            parents = data["derived-from"]
            if parents and "label" in parents[0]:
                return parents[0]["label"]
        
        # Otherwise, keep digging into the values
        for value in data.values():
            result = find_parent_label(value)
            if result:
                return result
                
    elif isinstance(data, list):
        for item in data:
            result = find_parent_label(item)
            if result:
                return result
                
    return None


session = requests.Session()  # Use a session for connection pooling

def normalize_name(name):
    """Removes all non-alphanumeric characters and converts to lowercase."""
    return re.sub(r'[^a-zA-Z0-9]', '', name).lower()

def cross_check_cell_line(entity_name, is_retry=False):
    base_url = "https://api.cellosaurus.org/search/cell-line"
    # Using 'q' for a broader search on retry, 'id' for exact on first pass
    query = {entity_name} if not is_retry else entity_name
    params = {"q": query, "format": "json"}

    try:
        response = session.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        result_list = data.get("Cellosaurus", {}).get("cell-line-list", [])

        if not result_list:
            return f"No matches found for {entity_name}."

        first_match = result_list[0]

       

        parsed_results = {}

        # 1. Basic IDs
        cvcl_list = first_match.get("accession-list", [])
        parsed_results['CVCL_ID'] = cvcl_list[0].get("value") if cvcl_list else None
        parsed_results['Cellosaurus_URL'] = f"https://www.cellosaurus.org/{parsed_results['CVCL_ID']}" if parsed_results['CVCL_ID'] else None

        # 2. Find ATCC Data
        atcc_entry = find_atcc_data(first_match)
        
        # 3. Handle Fallback Logic
        if atcc_entry:
            parsed_results['ATCC_ID'] = atcc_entry.get("accession")
            parsed_results['ATCC_URL'] = f"https://www.atcc.org/products/{parsed_results['ATCC_ID']}"
            # Use parent label as canonical name if available
            parent_label = find_parent_label(first_match)
            parsed_results['canonical_name'] = parent_label if parent_label else entity_name
        else:
            # NO ATCC found. Check for a parent/canonical name to retry.
            parent_label = find_parent_label(first_match)
            
            if parent_label and parent_label.lower() != entity_name.lower() and not is_retry:
                # RECURSIVE CALL: Try again using the parent name
                return cross_check_cell_line(parent_label, is_retry=True)
            else:
                # No parent found or already retried; return what we have
                parsed_results['ATCC_ID'] = None
                parsed_results['ATCC_URL'] = None
                parsed_results['canonical_name'] = entity_name

        return parsed_results

    except Exception as e:
        return f"Error querying Cellosaurus for {entity_name}: {str(e)}"

start = time.time()

#results = (cross_check_cell_line("LS-180"))
#print(results)
#print("Time taken for Cellosaurus check:", time.time() - start)


def check_uniprot(name):
    """Returns UniProt ID if name is a protein/gene, else None."""
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {"query": f"gene_exact:{name} OR protein_name:\"{name}\" AND reviewed:true AND organism_id:9606", "format": "json", "size": 5}
    try:
        res = session.get(url, params=params, timeout=5)
        res.raise_for_status()
        data = res.json()

        if not data.get("results"):
            return None

        result = data["results"][0]
        

        # --- VALIDATION STEP ---
        
        name_upper = name.upper()

        for entry in data["results"]:
            all_possible_names = []

            # A. Collect all Gene Names (Primary, Synonyms, ORF, Locus)
            for gene in entry.get("genes", []):
                all_possible_names.append(gene.get("geneName", {}).get("value", "").upper())
                for syn in gene.get("synonyms", []):
                    all_possible_names.append(syn.get("value", "").upper())

            # B. Collect all Protein Names (Recommended, Alternative)
            desc = entry.get("proteinDescription", {})
            
            # Recommended Name
            rec_name = desc.get("recommendedName", {})
            all_possible_names.append(rec_name.get("fullName", {}).get("value", "").upper())
            for sn in rec_name.get("shortNames", []):
                all_possible_names.append(sn.get("value", "").upper())
            
            # Alternative Names (Common synonyms)
            for alt in desc.get("alternativeNames", []):
                all_possible_names.append(alt.get("fullName", {}).get("value", "").upper())
                for sn in alt.get("shortNames", []):
                    all_possible_names.append(sn.get("value", "").upper())

            # C. The Validation Check
            # Remove empty strings and check if our 'name' is in the list
            if name_upper in [n for n in all_possible_names if n]:
                return entry.get("primaryAccession")

    except exception as e:
        print(f"Error checking UniProt for {name}: {str(e)}")
        return None
    return None

print("Testing UniProt check with 'SHP2':", check_uniprot("SHP2"))


print("Cross-checking extracted entities with PubChem...")

for (entity_text, entity_label), count in tqdm(entity_counts.items()):
    try:
        # Search PubChem for the entity text
        results = pcp.get_compounds(entity_text, 'name')
        
        if results:
            validated_drugs[entity_text] = {
                'label': entity_label,
                'count': count,
                'pubchem_id': results[0].cid,
                "pubchem_url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{results[0].cid}"
            }
            print(f"Validated: {entity_text} -> PubChem CID: {results[0].cid}")
            continue

        
        cell_info = cross_check_cell_line(entity_text)
        if cell_info and isinstance(cell_info, dict):
            validated_drugs[entity_text] = {
                'label': entity_label,
                'count': count,
                'pubchem_id': None,
                'cellosaurus_info': cell_info
            }
            print(f"Validated as cell line: {entity_text} -> Cellosaurus info: {cell_info}")
            continue

        if check_uniprot(entity_text):
            validated_drugs[entity_text] = {
                'label': entity_label,
                'count': count,
                'pubchem_id': None,
                'uniprot_id': check_uniprot(entity_text)
            }
            print(f"Validated as protein/gene: {entity_text} -> UniProt ID: {check_uniprot(entity_text)}")
            continue


        if pcp.get_substances(entity_text, 'name'):
            validated_drugs[entity_text] = {
                'label': entity_label,
                'count': count,
                'pubchem_id': None,
                'pubchem_substance': True
            }
            print(f"Validated as substance: {entity_text} -> Found in PubChem Substances")
            continue
 
        else: 

            validated_drugs[entity_text] = {
                'label': entity_label,
                'count': count,
                'pubchem_id': None
            }
            print(f"Not found in PubChem: {entity_text}")

    except Exception as e:
        print(f"Error validating {entity_text}: {e}")
        validated_drugs[entity_text] = {
            'label': entity_label,
            'count': count,
            'pubchem_id': None,
            'error': str(e)
        }
    time.sleep(0.5)  # Sleep to avoid hitting PubChem rate limits

with open("validated_drugs.json", "w") as f:
    json.dump(validated_drugs, f, indent=4)

'''
def agent_verify_biomed(entity_name):

    # Define your "Ground Truth" buckets
    candidate_labels = [
        "therapeutic drug or inhibitor", 
        "experimental cell line", 
        "laboratory buffer or reagent", 
        "protein or genetic mutation",
        "other"
    ]
    
    # This template forces the NLI model to check if the entity fits the category
    hypothesis_template = "This is a {}."
    
    result = nli_classifier(
        clean_name, 
        candidate_labels, 
        hypothesis_template=hypothesis_template
    )
    
    # Return the label with the highest logical 'entailment' score
    return result['labels'][0]

for i, (entity, count) in enumerate(entity_counts.items()):
    #if i ==2:
    #    break
    entity_name, entity_label = entity
    verified_label = agent_verify_biomed(entity_name)
    print(f"{entity_name} ({entity_label}) -> Verified as: {verified_label}")



# Step 3 - Dynamic Second Pass

new_labels = list(set(refined_mapping.values()))

final_entities = []
for section in sections:
    text = section['section_text']
    text_sections = text.split("\n\n")

    for text_section in text_sections:
        section_entities = model.predict_entities(text_section, new_labels)
        final_entities.extend(section_entities)


#print unique entities from final pass
final_unique_entities = {(entity['text'], entity['label']) for entity in final_entities}
print("Final Unique Entities:")
for entity in final_unique_entities:
    print(f"{entity[0]} ({entity[1]})")
'''