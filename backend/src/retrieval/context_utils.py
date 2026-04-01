import re

def get_context(text, value, window=100):
    matches = [m.start() for m in re.finditer(re.escape(value), text, re.IGNORECASE)]
    contexts = []

    for idx in matches:
        start = max(0, idx - window)
        end = min(len(text), idx + window)
        contexts.append(text[start:end])

    return contexts