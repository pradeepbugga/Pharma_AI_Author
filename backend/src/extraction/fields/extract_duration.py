import re
from backend.src.utils.llm import call_llm
from backend.src.retrieval.context_utils import get_context
from collections import defaultdict

# this script is used to extract and normalize treatment duration information for in vivo studies.

# First we use regex to identify candidate duration phrases in the text
DURATION_PATTERNS = [
    r"\d+\s+days",
    r"\d+-day",
    r"\d+\s+weeks",
    r"up to\s+\d+\s+days",
    r"after\s+\d+\s+days",
    r"\d+\s+consecutive\s+doses",
    r"bid\s*[×x]\s*\d+\s+days",
    r"\d+\s+days\s+off",
    r"\d+\s+days\s+on"
]

def extract_duration_candidates(text):
    matches = []

    for pattern in DURATION_PATTERNS:
        matches += re.findall(pattern, text, re.IGNORECASE)

    return list(set(matches))

# next we get the context (text snippets) around the identified candidates to pass to LLM

def get_duration_contexts(text, candidates):
    results = []

    for c in candidates:
        ctx = get_context(text, c, window=120)
        results.append({
            "value": c,
            "context": ctx
        })

    return results

# then we call the LLM to classify the duration for each candidate
# we use the identified drug name, the candidate duration phrases, the context around those phrases, and the administration and dosage contexts as additional information 


def extract_duration_LLM(drug_name, duration_candidates, duration_context, admin_chunks, context_memory_administration, context_memory_dosage):
    prompt = f"""

    You are validating in vivo dosing information for a drug.

    Drug:
    {drug_name}

    Candidate durations:
    {duration_candidates}

    Duration contexts:
    {duration_context}

    Administration snippets:
    {admin_chunks}

    Context (from administration detection):
    {context_memory_administration}

    Context (from dose detection):
    {context_memory_dosage}

    Task:
    Classify as ONE of:

    - administration_duration → total treatment duration (e.g., 7 days, 28 days)
    - dosing_schedule → pattern (e.g., 5 days off, BID × 7 days)
    - dosing_count → number of doses (e.g., 5 consecutive doses)
    - measurement_timepoint → assay or observation timing (NOT dosing)

    Rules:
    - “X days” with dosing → administration_duration
    - “X days off” → dosing_schedule
    - “X consecutive doses” → dosing_count
    - “3-day screen” → measurement_timepoint

    Confidence scoring:
    - 1.0 (Certain): The text explicitly links the duration to a dosing verb (e.g., "Mice were administered {drug_name} daily for 28 days").
    - 0.8 (High): The duration is mentioned in a sentence describing a clear treatment outcome (e.g., "After 14 days of {drug_name} treatment, tumor volume decreased...").
    - 0.5 (Medium): A time period is mentioned (e.g., "7 days"), but it's unclear if it refers to the treatment duration or the time until the first measurement.
    - 0.3 (Low): The time period is associated with a baseline or a control group, not necessarily the {drug_name} treatment.
    - 0.1 (Critically Low): The duration refers to an incubation period (in vitro) or a post-treatment "washout" period.


    Return JSON:
    {{
      "classification": "...",
      "evidence": "...",
      "confidence": 0-1
    }}
    """

    return call_llm(prompt)


# The result of the above function will have duplicates and variations of the same duration (e.g., "7 days", "after 7 days", "up to 7 days").
# So below we have another LLM call that normalizes the durations
# we group the durations from above by classification (grouped_data) 
# then we also pass the full results from the above LLM call below
# the confidence scoring rules below are more like "consistency" scores

def normalize_durations(grouped_data, context_memory):
 
  prompt = f"""
  You are a STRICT data normalization system.

  You MUST ONLY transform the provided input values.
  You MUST NOT invent, infer, generalize, or add any new values.

  Input Data:
  {grouped_data}

  Context:
  {context_memory}

  Task:

  1. Normalize formatting:
    - lowercase all text
    - standardize spacing (e.g., "7 Days" → "7 days")
    - remove prefixes like "after ", "up to " if present

  2. Deduplicate:
    - if multiple entries refer to the same concept (e.g., "7 days", "after 7 days"), keep ONE canonical form

  3. Preserve meaning:
    - DO NOT change semantics
    - DO NOT convert values (e.g., do NOT create "14 days" unless it exists in input)

  4. Preserve categories:
    - keep the same top-level keys
    - DO NOT add new categories

  Rules:
  - Every output value MUST map to at least one input value
  - If a value cannot be mapped directly to input, REMOVE it
  - DO NOT create new values under any circumstance
  - Evidence must be verbatim text from the paper.
  - No meta-language ("the phrase", "this describes", etc.)

  Optional:
  - You may merge patterns:
    "2 treatment days followed by 5 days off" → "2 days on / 5 days off"

  Final Confidence Scoring:
    Calculate the final 'confidence' (0.0 - 1.0) for each normalized value based on:
    
    1. AGREEMENT (+0.2): If the same value is found in BOTH 'admin_chunks' and 'duration_context', increase confidence.
    2. CONTRADICTION (-0.4): If one snippet says "7 days" and another says "14 days", you must pick the most evidenced one but heavily penalize confidence.
    3. MEMORY ALIGNMENT (+0.1): If the duration matches the 'dosage' context (e.g., "10 doses" matches "5 days BID"), increase confidence.
    4. VERBATIM PENALTY (-0.3): If the value was inferred from a measurement timepoint rather than an administration statement.

    SCORING KEY:
    - 0.9 - 1.0: Explicit, repeated, and matches the dosage schedule perfectly.
    - 0.7 - 0.8: Found once in a clear administration context.
    - 0.5 - 0.6: Inferred from a result (e.g., "tumor regression at day 14").
    - < 0.4: Conflicting data or heavily reliant on ambiguous snippets.


  Output Format:
    Return JSON where each category is a list of objects:
    {{
      "administration_duration": [
        {{
          "normalized_value": "X days",
          "evidence": "...",
          "logic": " ... how well it matches..."
          "source_confidecne": [X, Y, Z],  # confidence from each individual snippet
          "confidence": 0-1 
        }}
      ],
      ...
    }}
  """
  return call_llm(prompt)

def extract_duration(primary_drug, context_data, admin_chunks, admin_results, dose_results):
    duration_contexts = context_data["duration_contexts"]
    full_metadata = []

    for item in duration_contexts:
        candidate = item["value"]
        snippet = item["context"]
        
        llm_output = extract_duration_LLM(primary_drug, candidate, snippet, admin_chunks, admin_results, dose_results)

        classification = llm_output["classification"]

        # Preserve the full record
        record = {
            "value": item["value"], # The raw candidate
            "classification": llm_output["classification"],
            "evidence": llm_output.get("evidence", ""),
            "confidence": llm_output.get("confidence", 0)
        }
        full_metadata.append(record)

    # Call the new deterministic function with the full objects
    return normalize_durations_deterministic(full_metadata)


# below are deterministic normalization functions to be used instead of 
# the above LLM-based normalization if we want to be more strict and transparent in how we normalize the durations.

def normalize_duration_value(raw):
    match = re.search(r"\d+", raw.lower())
    if not match:
        return None
    return f"{int(match.group())} days"


def normalize_durations_deterministic(full_metadata):
    """
    Groups by classification, normalizes values, and maintains 
    all source evidence and confidence scores.
    """
    structured_output = {}

    for record in full_metadata:
        category = record["classification"]
        raw_val = record["value"]
        
        # 1. Normalize the value (e.g., "After 7 Days" -> "7 days")
        norm_val = normalize_duration_value(raw_val)
        if not norm_val:
            continue

        # 2. Initialize category and normalized bucket
        if category not in structured_output:
            structured_output[category] = {}
        
        if norm_val not in structured_output[category]:
            structured_output[category][norm_val] = {
                "normalized_value": norm_val,
                "evidence_list": [],
                "source_confidences": [],
                "raw_values": set()
            }

        # 3. Attach the provenance data
        structured_output[category][norm_val]["evidence_list"].append(record["evidence"])
        structured_output[category][norm_val]["source_confidences"].append(record["confidence"])
        structured_output[category][norm_val]["raw_values"].add(raw_val)

    # 4. Final Format (Sort and flatten)
    final_results = {}
    for category, norm_map in structured_output.items():
        # Numerical sort by the days in the key
        sorted_keys = sorted(norm_map.keys(), key=lambda x: int(re.search(r"\d+", x).group()))
        
        final_results[category] = []
        for key in sorted_keys:
            entry = norm_map[key]
            final_results[category].append({
                "normalized_value": entry["normalized_value"],
                "evidence": " | ".join(list(set(entry["evidence_list"]))), # Deduplicated snippets
                "confidence": max(entry["source_confidences"]), # Or average
                "debug_raw_source": list(entry["raw_values"])
            })

    return final_results