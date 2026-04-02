import re

# this script is used to clean up LaTeX formatting in biomedical text

def clean_biomedical_text(text):
    if not text:
        return ""

    # Handle the double-backslash LaTeX common in JSON strings
    # This targets: $^{\mathrm{G12D}}$, ^{\mathrm{G12D}}, or ^{G12D}
    # It converts them all to a simple dash + the mutation: -G12D
    text = re.sub(r'\$?\^\{(\\mathrm\{)?(.*?)\}?\}\$?', r'-\2', text)

    # Specifically target the common "PI3K$\alpha$" pattern
    # The double backslash in JSON is actually a single backslash in the string
    text = re.sub(r'\\alpha', 'alpha', text)
    text = re.sub(r'\\beta', 'beta', text)

    # Clean up any remaining LaTeX/Math leftovers
    # Remove $, \, {, }
    text = re.sub(r'[\$\{\}\\]', '', text)
    
    # Remove common formatting and citations
    text = re.sub(r'\\textit\{', '', text) # Remove italic start
    text = re.sub(r'~', ' ', text)          # Non-breaking space
    
    # Final whitespace cleanup
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text