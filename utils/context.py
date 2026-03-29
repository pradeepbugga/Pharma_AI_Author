
import re

def get_entity_context(entity: str, text: str, window=1):
    """
    Returns sentence containing entity + optional neighbors
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)

    hits = []
    for i, s in enumerate(sentences):
        if entity.lower() in s.lower():
            left = sentences[i-1] if i > 0 else ""
            right = sentences[i+1] if i < len(sentences)-1 else ""

            context = " ".join([left, s, right]) if window else s
            hits.append(context)

    return hits[:2]  # keep small