import re
from typing import List, Dict


def split_into_chunks(text: str, max_len: int = 400) -> List[str]:
    """
    Split text into paragraph-like chunks.
    """
    paragraphs = re.split(r'\n\s*\n', text)

    chunks = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue

        # further split long paragraphs
        if len(p) > max_len:
            sentences = re.split(r'(?<=[.!?])\s+', p)
            current = ""
            for s in sentences:
                if len(current) + len(s) < max_len:
                    current += " " + s
                else:
                    chunks.append(current.strip())
                    current = s
            if current:
                chunks.append(current.strip())
        else:
            chunks.append(p)

    return chunks


def score_chunk(chunk: str, drug: str, keywords: List[str]) -> float:
    """
    Score chunk based on:
    - drug presence (high weight)
    - keyword presence
    - proximity between drug and keywords
    """
    chunk_lower = chunk.lower()
    drug_lower = drug.lower()

    score = 0.0

    # 1. drug presence (required signal)
    if drug_lower in chunk_lower:
        score += 3.0
    else:
        return 0.0  # hard filter: must contain drug

    # 2. keyword matches
    for kw in keywords:
        if kw in chunk_lower:
            score += 1.0

            # 3. proximity bonus
            drug_idx = chunk_lower.find(drug_lower)
            kw_idx = chunk_lower.find(kw)

            if drug_idx != -1 and kw_idx != -1:
                distance = abs(drug_idx - kw_idx)
                if distance < 100:
                    score += 1.0
                elif distance < 200:
                    score += 0.5

    return score

def retrieve_chunks(
    text: str,
    query: List[str],
    drug: str,
    top_k: int = 8
) -> List[Dict]:
    """
    Retrieve top-k chunks relevant to drug usage context.
    """
    chunks = split_into_chunks(text)

    keywords = [q.lower() for q in query if q.lower() != drug.lower()]

    scored = []
    for chunk in chunks:
        s = score_chunk(chunk, drug, keywords)
        if s > 0:
            scored.append({
                "text": chunk,
                "score": s
            })

    # sort by score
    scored = sorted(scored, key=lambda x: x["score"], reverse=True)

    return scored[:top_k]