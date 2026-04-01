from backend.src.utils.llm import call_llm


# this function is used to detect the broad objectives of the study based on the text evidence.
# it takes drug name identified along with abstract and discussion text

def extract_objectives(drug_name, abstract_discussion_text):
    prompt = f"""

    Summarize the broad objective of the study in 1–2 sentences.
    

    You MUST include:
    - drug name
    - molecular target (if applicable)
    - modality 
    - biological systems studied
    - high-level study endpoints

    You MUST NOT include:
    - detailed binding mechanisms
    - assay-specific details
    - speculative or inferred information
        
    Drug: 
    {drug_name}

    Context:
    {text}

    Rules:
    - Do NOT use vague phrases like "specific protein"
    - Start with "To evaluate..." or "To characterize..."
    - Use a single main clause ("To evaluate..." or "To characterize...")
    - Be scientifically precise
    - Do NOT invent information not present in the text
    - Focus on WHAT is being evaluated, not HOW at a molecular level
    - Focus on broad purpose, not exhaustive detail


    Return only the objective sentence as string in JSON format:
    {{
    "objective": "..."
    }}
    """
    return call_llm(prompt)

