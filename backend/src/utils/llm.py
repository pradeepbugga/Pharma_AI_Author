
import json, re
from openai import OpenAI
import os
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv

# this script calls LLM (we use Kimi K2) with a given prompt
# we use the functino for all our LLM calls in this project
# we also use tenacity to implement retries with exponential backoff in case of rate limits or transient errors


load_dotenv()  # Load environment variables from .env file

API_KEY = os.getenv("KIMI_K_API_KEY")


client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.moonshot.ai/v1")


def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError("No JSON found")


# use retry decorator here for Tenacity

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception)
)
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
        if "429" in str(e):
            raise Exception("Rate limit hit, retrying...")


        return {
            "error": str(e),
            "raw": content if 'content' in locals() else None
        }