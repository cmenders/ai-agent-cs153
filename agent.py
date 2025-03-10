import os
import re
from bibliography import Bibliography
import discord
from mistralai import Mistral
import asyncio
import json
from mistralai.models.sdkerror import SDKError
from citation_formatter import get_available_styles
from research_notes import ResearchNotes


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
        self.bibliography = Bibliography()
        self.notes = ResearchNotes()

    async def run(self, message: discord.Message):
        # Handle note commands
        note_command = self.check_for_note_command(message.content)
        if note_command:
            return await self.handle_note_command(message, note_command)
        
        # Handle citation formatting commands
        if re.search(r'\b(cite|format|citation)\s+(?:paper)?\s*(\d+)?\s+(?:in|as|using)?\s+([a-zA-Z]+)(?:\s+format|style)?\b', message.content.lower()):
            return await self.handle_citation_command(message)
        
        # Handle bibliography requests
        if re.search(r'\b(give|show|display|present|list)\s+(?:me\s+)?(?:the\s+)?(bibliography|citations|references)(?:\s+in\s+([a-zA-Z]+)(?:\s+format|style)?)?', message.content.lower()):
            return self.handle_bibliography_command(message)
        
        # Handle paper list requests
        if re.search(r'\b(list|show|give|display)\s+(?:me\s+)?(?:the\s+)?(?:cited\s+)?papers\b', message.content.lower()):
            return self.split_message(self.bibliography.get_paper_list())
        
        # Handle citation styles listing
        if re.search(r'\b(what|which|list|show)\s+(?:are\s+)?(?:the\s+)?(?:available\s+)?citation\s+(?:styles|formats)\b', message.content.lower()):
            styles = get_available_styles()
            return [f"Available citation styles: {', '.join(style.upper() for style in styles)}"]

        # Original message processing
        is_research = await is_research_query(self.client, message.content)

        if is_research:
            search_query = await extract_search_query(self.client, message.content)
            if search_query:
                await message.channel.send(f"Searching for: '{search_query}'...")
                search_results = await search_google_scholar(search_query)
                formatted_results = await format_search_results(search_query, search_results)
                system_content = f"You are a research assistant. Answer based on these papers:\n\n{formatted_results}"

                # Add papers to bibliography
                for paper in search_results:
                    self.bibliography.add_paper(paper)
            else:
                system_content = "You are a research assistant. The user has a research query."
        else:
            system_content = "You are a helpful assistant."

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": message.content},
        ]

        retries = 5  # Max retries
        delay = 2  # Initial delay in seconds

        for attempt in range(retries):
            try:
                response = await self.client.chat.complete_async(
                    model=MISTRAL_MODEL,
                    messages=messages
                )
                content = response.choices[0].message.content
                return self.split_message(content)

            except SDKError as e:
                error_data = json.loads(str(e).replace("SDKError: ", "").strip())
                if "Requests rate limit exceeded" in error_data.get("message", ""):
                    if attempt < retries - 1:
                        print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                        await asyncio.sleep(delay)
                        delay *= 2  # Exponential backoff
                    else:
                        print("Max retries reached. Unable to process request.")
                        return ["Rate limit exceeded. Please try again later."]
                else:
                    raise e  # Re-raise other errors
    
    def check_for_note_command(self, message_content):
        """Check if the message contains a note command and return the type of command"""
        
        # Check for add note command
        add_match = re.search(r'\b(?:add|create)\s+(?:a\s+)?note\s+(?:to|for)\s+paper\s+(\d+)\s*(?::|-)?\s*(.*)', message_content, re.IGNORECASE | re.DOTALL)
        if add_match:
            return {
                "command": "add",
                "paper_index": add_match.group(1),
                "note_text": add_match.group(2).strip()
            }
        
        # Check for view notes command for a specific paper
        view_paper_match = re.search(r'\b(?:view|show|get|display)\s+(?:the\s+)?notes\s+(?:for|on)\s+paper\s+(\d+)', message_content, re.IGNORECASE)
        if view_paper_match:
            return {
                "command": "view",
                "paper_index": view_paper_match.group(1)
            }
        
        # Check for view all notes command
        view_all_match = re.search(r'\b(?:view|show|get|display)\s+(?:all\s+)?(?:my\s+)?(?:research\s+)?notes', message_content, re.IGNORECASE)
        if view_all_match:
            return {
                "command": "view_all"
            }
        
        # Check for delete note command
        delete_match = re.search(r'\b(?:delete|remove)\s+note\s+(\d+)\s+(?:from|for)\s+paper\s+(\d+)', message_content, re.IGNORECASE)
        if delete_match:
            return {
                "command": "delete",
                "note_index": delete_match.group(1),
                "paper_index": delete_match.group(2)
            }
        
        # Check for clear notes command
        clear_match = re.search(r'\b(?:clear|delete\s+all)\s+notes\s+(?:for|from)\s+paper\s+(\d+)', message_content, re.IGNORECASE)
        if clear_match:
            return {
                "command": "clear",
                "paper_index": clear_match.group(1)
            }
        
        # Check for clear all notes command
        clear_all_match = re.search(r'\b(?:clear|delete)\s+all\s+(?:my\s+)?(?:research\s+)?notes', message_content, re.IGNORECASE)
        if clear_all_match:
            return {
                "command": "clear_all"
            }
        
        return None

    async def handle_note_command(self, message, command_info):
        """Handle note commands"""
        conversation_id = str(message.channel.id)
        
        # Add note to a paper
        if command_info["command"] == "add":
            paper_index = command_info["paper_index"]
            note_text = command_info["note_text"]
            
            if not note_text:
                return ["Please provide the note text. Example: 'add note to paper 1: This paper has interesting methodology.'"]
            
            paper_key, paper = self.bibliography.get_paper_by_index(paper_index)
            if not paper_key:
                return [f"Paper {paper_index} not found. Use 'list papers' to see available papers."]
            
            success = self.notes.add_note(conversation_id, paper_key, note_text)
            if success:
                paper_title = self.bibliography.get_paper_title(paper_key)
                return [f"✓ Note added to paper: {paper_title}"]
            else:
                return ["⚠ Failed to add note. Please try again."]
        
        # View notes for a specific paper
        elif command_info["command"] == "view":
            paper_index = command_info["paper_index"]
            paper_key, paper = self.bibliography.get_paper_by_index(paper_index)
            
            if not paper_key:
                return [f"Paper {paper_index} not found. Use 'list papers' to see available papers."]
            
            paper_info = self.bibliography.get_paper_info_dict()
            formatted_notes = self.notes.format_notes(conversation_id, paper_key, paper_info)
            return self.split_message(formatted_notes)
        
        # View all notes
        elif command_info["command"] == "view_all":
            paper_info = self.bibliography.get_paper_info_dict()
            formatted_notes = self.notes.format_notes(conversation_id, paper_info=paper_info)
            return self.split_message(formatted_notes)
        
        # Delete a specific note
        elif command_info["command"] == "delete":
            note_index = int(command_info["note_index"]) - 1  # Convert to 0-based index
            paper_index = command_info["paper_index"]
            
            paper_key, paper = self.bibliography.get_paper_by_index(paper_index)
            if not paper_key:
                return [f"Paper {paper_index} not found. Use 'list papers' to see available papers."]
            
            success = self.notes.delete_note(conversation_id, paper_key, note_index)
            if success:
                paper_title = self.bibliography.get_paper_title(paper_key)
                return [f"✓ Note {note_index + 1} deleted from paper: {paper_title}"]
            else:
                return [f"⚠ Note {note_index + 1} not found for paper {paper_index}."]
        
        # Clear notes for a specific paper
        elif command_info["command"] == "clear":
            paper_index = command_info["paper_index"]
            paper_key, paper = self.bibliography.get_paper_by_index(paper_index)
            
            if not paper_key:
                return [f"Paper {paper_index} not found. Use 'list papers' to see available papers."]
            
            success = self.notes.clear_notes(conversation_id, paper_key)
            if success:
                paper_title = self.bibliography.get_paper_title(paper_key)
                return [f"✓ All notes cleared for paper: {paper_title}"]
            else:
                return ["⚠ Failed to clear notes. Please try again."]
        
        # Clear all notes
        elif command_info["command"] == "clear_all":
            success = self.notes.clear_notes(conversation_id)
            if success:
                return ["✓ All research notes have been cleared."]
            else:
                return ["⚠ Failed to clear notes. Please try again."]
        
        return ["Unknown note command. Please try again."]

    async def handle_citation_command(self, message):
        # Extract paper index and citation style from the message
        match = re.search(r'\b(cite|format|citation)\s+(?:paper)?\s*(\d+)?\s+(?:in|as|using)?\s+([a-zA-Z]+)(?:\s+format|style)?\b', message.content.lower())
        
        if not match:
            return ["Please specify a paper number and citation style. Example: 'cite paper 1 in APA'"]
        
        paper_index = match.group(2)
        style = match.group(3)
        
        # If paper index is not provided, return help message
        if not paper_index:
            return ["Please specify a paper number. Example: 'cite paper 1 in APA'"]
        
        # Get the formatted citation
        citation = self.bibliography.get_citation(paper_index, style)
        return [citation]
    
    def handle_bibliography_command(self, message):
        # Extract citation style from the message if provided
        match = re.search(r'\b(bibliography|citations|references)(?:\s+in\s+([a-zA-Z]+)(?:\s+format|style)?)?', message.content.lower())
        
        style = "apa"  # Default style
        if match and match.group(2):
            style = match.group(2)
        
        return self.split_message(self.bibliography.get_formatted_bibliography(style))

    def split_message(self, content):
        if len(content) <= 2000:
            return [content]
        
        chunks = []
        while len(content) > 2000:
            split_index = content.rfind('\n', 0, 2000)
            if split_index == -1:  # If no newline found, force split at 2000
                split_index = 2000
            
            chunks.append(content[:split_index])
            content = content[split_index:].lstrip()
        
        if content:
            chunks.append(content)
        
        return chunks