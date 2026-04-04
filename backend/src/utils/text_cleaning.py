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

import re
import html

def normalize_latex_to_html(text):
    if not text or not isinstance(text, str):
        return text

    # --- short-circuit if already clean (cheap optimization) ---
    if "<sup>" in text or "<sub>" in text:
        # still need to clean LaTeX remnants if mixed
        pass

    # --- protect existing HTML tags ---
    text = text.replace("<sup>", "___SUP_OPEN___")
    text = text.replace("</sup>", "___SUP_CLOSE___")
    text = text.replace("<sub>", "___SUB_OPEN___")
    text = text.replace("</sub>", "___SUB_CLOSE___")

    # --- escape everything else ---
    text = html.escape(text)

    # --- restore HTML tags ---
    text = text.replace("___SUP_OPEN___", "<sup>")
    text = text.replace("___SUP_CLOSE___", "</sup>")
    text = text.replace("___SUB_OPEN___", "<sub>")
    text = text.replace("___SUB_CLOSE___", "</sub>")

    # --- LaTeX → HTML conversions ---

    # superscripts (with \mathrm)
    text = re.sub(
        r"\$?\^\{\\mathrm\{([^}]+)\}\}\$?",
        r"<sup>\1</sup>",
        text
    )

    # superscripts generic
    text = re.sub(
        r"\$?\^\{([^}]+)\}\$?",
        r"<sup>\1</sup>",
        text
    )

    # subscripts
    text = re.sub(
        r"\$?_\{([^}]+)\}\$?",
        r"<sub>\1</sub>",
        text
    )

    # IC50 variants → canonical
    text = re.sub(r"IC[_\s]?50", r"IC<sub>50</sub>", text)

    # remove leftover math markers
    text = text.replace("$", "")

    return text