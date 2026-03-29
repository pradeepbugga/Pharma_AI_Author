# utils/llm.py

import json, re
from openai import OpenAI
import os

API_KEY = os.getenv("KIMI_K_API_KEY")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.moonshot.ai/v1")



def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError("No JSON found")


def call_llm(prompt: str, model="kimi-k2-turbo-preview"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You output ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        # robust JSON extraction
        return extract_json(content)

    except Exception as e:
        return {
            "error": str(e),
            "raw": content if 'content' in locals() else None
        }