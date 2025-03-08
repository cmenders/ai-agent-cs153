import os
import discord
from mistralai import Mistral

from query_processing import is_research_query, extract_search_query
from scholar_search import search_google_scholar, format_search_results

MISTRAL_MODEL = "mistral-large-latest"
SYSTEM_PROMPT = """
You are a helpful research assistant chatbot. 
Your primary role is to help users find academic research papers, summarize key information, and provide relevant context.
When users ask research questions, try to:
1. Identify the research topic or question
2. Search Google Scholar for relevant academic papers
3. Summarize the key findings from the papers found
4. Include the title, authors, year, number of citations, and a link/url to the paper
4. Explain how these papers relate to the user's question

Keep your answers concise and focused on the most important information.
Do not fabricate paper titles, authors, or citations. Only provide information that is included in the search results.
"""


class MistralAgent:
    def __init__(self):
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
        self.client = Mistral(api_key=MISTRAL_API_KEY)

    async def run(self, message: discord.Message):
        is_research = await is_research_query(self.client, message.content)
        
        if is_research:
            search_query = await extract_search_query(self.client, message.content)
            if search_query:
                await message.channel.send(f"Searching for: '{search_query}'...")
                search_results = await search_google_scholar(search_query)
                formatted_results = await format_search_results(search_query, search_results)
                system_content = f"You are a research assistant. Answer based on these papers:\n\n{formatted_results}"
            else:
                system_content = "You are a research assistant. The user has a research query."
        else:
            system_content = "You are a helpful assistant."
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": message.content},
        ]
        response = await self.client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=messages
        )
        content = response.choices[0].message.content
        return content