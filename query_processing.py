import json
from mistralai import Mistral

MISTRAL_MODEL = "mistral-large-latest"

async def is_research_query(client, msgContent: str) -> bool:
    prompt = """
    Determine if the following message is requesting info about academic research or scholarly papers.
    Return a JSON response with a single key "is_research" with value true or false.
    """
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": msgContent}
    ]
    response = await client.chat.complete_async(
        model=MISTRAL_MODEL,
        messages=messages,
        response_format={"type": "json_object"}
    )
    try:
        result = response.choices[0].message.content
        parsed = json.loads(result)
        return parsed.get("is_research", False)
    except:
        return False


async def extract_search_query(client, msgContent: str) -> str:
    prompt = """
    Extract a search query for Google Scholar from the following message.
    Return a JSON response with a single key "search_query" which contains the search terms to use.
    Make the search query specific but concise (5-8 words maximum).
    """
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": msgContent}
    ]
    response = await client.chat.complete_async(
        model=MISTRAL_MODEL,
        messages=messages,
        response_format={"type": "json_object"}
    )
    try:
        result = response.choices[0].message.content
        parsed = json.loads(result)
        return parsed.get("search_query", "")
    except:
        return "" 