import os
import discord
import logging

from discord.ext import commands
from dotenv import load_dotenv
from agent import MistralAgent
from citation_formatter import get_available_styles

PREFIX = "!"

# Setup logging
logger = logging.getLogger("discord")

# Load the environment variables
load_dotenv()

# Create the bot with all intents
# The message content and members intent must be enabled in the Discord Developer Portal for the bot to work.
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# Import the Mistral agent from the agent.py file
agent = MistralAgent()


# Get the token from the environment variables
token = os.getenv("DISCORD_TOKEN")


@bot.event
async def on_ready():
    """
    Called when the client is done preparing the data received from Discord.
    Prints message on terminal when bot successfully connects to discord.

    https://discordpy.readthedocs.io/en/latest/api.html#discord.on_ready
    """
    logger.info(f"{bot.user} has connected to Discord!")


@bot.event
async def on_message(message: discord.Message):
    """
    Called when a message is sent in any channel the bot can see.

    https://discordpy.readthedocs.io/en/latest/api.html#discord.on_message
    """
    # Don't delete this line! It's necessary for the bot to process commands.
    await bot.process_commands(message)

    # Ignore messages from self or other bots to prevent infinite loops.
    if message.author.bot or message.content.startswith("!"):
        return

    # Process the message with the agent you wrote
    # Open up the agent.py file to customize the agent
    logger.info(f"Processing message from {message.author}: {message.content}")
    
    # Show typing indicator while processing the request
    async with message.channel.typing():
        response = await agent.run(message)

    # Handle both single responses and response chunks
    if isinstance(response, list):
        # Send the first chunk as a reply
        await message.reply(response[0])
        
        # Send subsequent chunks as follow-up messages
        for chunk in response[1:]:
            await message.channel.send(chunk)
    else:
        # Send the response back to the channel
        await message.reply(response)


# Commands
@bot.command(name="ping", help="Pings the bot.")
async def ping(ctx, *, arg=None):
    if arg is None:
        await ctx.send("Pong!")
    else:
        await ctx.send(f"Pong! Your argument was {arg}")

@bot.command(name="cite", help="Formats a citation for a paper in the bibliography.")
async def cite(ctx, paper_index: int, style: str = "apa"):
    """
    Format a citation for a specific paper in the bibliography.
    
    Usage: !cite <paper_index> <style>
    Example: !cite 1 apa
    """
    citation = agent.bibliography.get_citation(paper_index, style)
    await ctx.send(citation)

@bot.command(name="bibliography", help="Shows the current bibliography in the specified format.")
async def bibliography(ctx, style: str = "apa"):
    """
    Show the current bibliography in the specified format.
    
    Usage: !bibliography <style>
    Example: !bibliography mla
    """
    bib = agent.bibliography.get_formatted_bibliography(style)
    
    # Split long messages
    chunks = agent.split_message(bib)
    for chunk in chunks:
        await ctx.send(chunk)

@bot.command(name="papers", help="Lists all cited papers.")
async def papers(ctx):
    """
    List all papers that have been cited in the conversation.
    
    Usage: !papers
    """
    paper_list = agent.bibliography.get_paper_list()
    await ctx.send(paper_list)

@bot.command(name="citation_styles", help="Lists all available citation styles.")
async def citation_styles(ctx):
    """
    List all available citation styles.
    
    Usage: !citation_styles
    """
    styles = get_available_styles()
    await ctx.send(f"Available citation styles: {', '.join(style.upper() for style in styles)}")

# Research Notes Commands
@bot.command(name="add_note", help="Add a note to a paper in the bibliography.")
async def add_note(ctx, paper_index: int, *, note_text):
    """
    Add a note to a specific paper.
    
    Usage: !add_note <paper_index> <note_text>
    Example: !add_note 1 This paper has an interesting methodology.
    """
    conversation_id = str(ctx.channel.id)
    paper_key, paper = agent.bibliography.get_paper_by_index(paper_index)
    
    if not paper_key:
        await ctx.send(f"Paper {paper_index} not found. Use !papers to see available papers.")
        return
    
    success = agent.notes.add_note(conversation_id, paper_key, note_text)
    
    if success:
        paper_title = agent.bibliography.get_paper_title(paper_key)
        await ctx.send(f"✓ Note added to paper: {paper_title}")
    else:
        await ctx.send("⚠ Failed to add note. Please try again.")

@bot.command(name="view_notes", help="View notes for a specific paper or all papers.")
async def view_notes(ctx, paper_index: int = None):
    """
    View notes for a specific paper or all papers.
    
    Usage: !view_notes [paper_index]
    Example: !view_notes 1
    """
    conversation_id = str(ctx.channel.id)
    paper_info = agent.bibliography.get_paper_info_dict()
    
    if paper_index is not None:
        paper_key, paper = agent.bibliography.get_paper_by_index(paper_index)
        if not paper_key:
            await ctx.send(f"Paper {paper_index} not found. Use !papers to see available papers.")
            return
        
        formatted_notes = agent.notes.format_notes(conversation_id, paper_key, paper_info)
    else:
        formatted_notes = agent.notes.format_notes(conversation_id, paper_info=paper_info)
    
    # Split long messages
    chunks = agent.split_message(formatted_notes)
    for chunk in chunks:
        await ctx.send(chunk)

@bot.command(name="delete_note", help="Delete a note from a paper.")
async def delete_note(ctx, paper_index: int, note_index: int):
    """
    Delete a specific note from a paper.
    
    Usage: !delete_note <paper_index> <note_index>
    Example: !delete_note 1 2
    """
    conversation_id = str(ctx.channel.id)
    paper_key, paper = agent.bibliography.get_paper_by_index(paper_index)
    
    if not paper_key:
        await ctx.send(f"Paper {paper_index} not found. Use !papers to see available papers.")
        return
    
    # Convert to 0-based index
    success = agent.notes.delete_note(conversation_id, paper_key, note_index - 1)
    
    if success:
        paper_title = agent.bibliography.get_paper_title(paper_key)
        await ctx.send(f"✓ Note {note_index} deleted from paper: {paper_title}")
    else:
        await ctx.send(f"⚠ Note {note_index} not found for paper {paper_index}.")

@bot.command(name="clear_notes", help="Clear all notes for a paper or all papers.")
async def clear_notes(ctx, paper_index: int = None):
    """
    Clear all notes for a specific paper or all papers.
    
    Usage: !clear_notes [paper_index]
    Example: !clear_notes 1
    """
    conversation_id = str(ctx.channel.id)
    
    if paper_index is not None:
        paper_key, paper = agent.bibliography.get_paper_by_index(paper_index)
        if not paper_key:
            await ctx.send(f"Paper {paper_index} not found. Use !papers to see available papers.")
            return
        
        success = agent.notes.clear_notes(conversation_id, paper_key)
        if success:
            paper_title = agent.bibliography.get_paper_title(paper_key)
            await ctx.send(f"✓ All notes cleared for paper: {paper_title}")
        else:
            await ctx.send("⚠ Failed to clear notes. Please try again.")
    else:
        success = agent.notes.clear_notes(conversation_id)
        if success:
            await ctx.send("✓ All research notes have been cleared.")
        else:
            await ctx.send("⚠ Failed to clear notes. Please try again.")

# Reading List Commands
@bot.command(name="reading_list", help="Manage reading lists.")
async def reading_list(ctx, action: str, name: str = None, paper_index: int = None):
    """
    Manage reading lists - create lists, add/remove papers, and view lists.
    
    Usage: !reading_list <action> [name] [paper_index]
    Actions: create, add, view, remove
    
    Examples:
    !reading_list create ML_Healthcare
    !reading_list add ML_Healthcare 3
    !reading_list view ML_Healthcare
    !reading_list view (shows all lists)
    !reading_list remove ML_Healthcare 2
    """
    conversation_id = str(ctx.channel.id)
    
    # Create a new reading list
    if action.lower() == "create" and name:
        success = agent.reading_lists.create_list(conversation_id, name)
        if success:
            await ctx.send(f"✓ Created reading list: {name}")
        else:
            await ctx.send(f"⚠ Reading list '{name}' already exists or could not be created.")
    
    # Add a paper to a reading list
    elif action.lower() == "add" and name and paper_index is not None:
        paper_key, paper = agent.bibliography.get_paper_by_index(paper_index)
        if not paper_key:
            await ctx.send(f"Paper {paper_index} not found. Use !papers to see available papers.")
            return
        
        success = agent.reading_lists.add_paper_to_list(conversation_id, name, paper_key)
        if success:
            paper_title = agent.bibliography.get_paper_title(paper_key)
            await ctx.send(f"✓ Added paper \"{paper_title}\" to reading list: {name}")
        else:
            await ctx.send(f"⚠ Reading list '{name}' not found or paper could not be added.")
    
    # View a specific reading list or all lists
    elif action.lower() == "view":
        paper_info = agent.bibliography.get_paper_info_dict()
        if name:
            formatted_list = agent.reading_lists.format_lists(conversation_id, name, paper_info)
        else:
            formatted_list = agent.reading_lists.format_lists(conversation_id)
        
        chunks = agent.split_message(formatted_list)
        for chunk in chunks:
            await ctx.send(chunk)
    
    # Remove a paper from a reading list
    elif action.lower() == "remove" and name and paper_index is not None:
        paper_key, paper = agent.bibliography.get_paper_by_index(paper_index)
        if not paper_key:
            await ctx.send(f"Paper {paper_index} not found. Use !papers to see available papers.")
            return
        
        success = agent.reading_lists.remove_paper_from_list(conversation_id, name, paper_key)
        if success:
            paper_title = agent.bibliography.get_paper_title(paper_key)
            await ctx.send(f"✓ Removed paper \"{paper_title}\" from reading list: {name}")
        else:
            await ctx.send(f"⚠ Reading list '{name}' not found or paper not in list.")
    
    # Delete a reading list
    elif action.lower() == "delete" and name:
        success = agent.reading_lists.delete_list(conversation_id, name)
        if success:
            await ctx.send(f"✓ Deleted reading list: {name}")
        else:
            await ctx.send(f"⚠ Reading list '{name}' not found.")
    
    else:
        await ctx.send("Invalid command. Use !help reading_list for usage information.")

@bot.command(name="related", help="Find papers related to a specific paper.")
async def related(ctx, paper_index: int, max_results: int = 5):
    """
    Find papers related to a specific paper based on title, authors, and content.
    
    Usage: !related <paper_index> [max_results]
    Example: !related 1 3
    """
    result = agent.bibliography.find_related_papers(paper_index, max_results)
    
    chunks = agent.split_message(result)
    for chunk in chunks:
        await ctx.send(chunk)

@bot.command(name="help", help="Shows detailed help information about bot commands and features.")
async def help_command(ctx, command: str = None):
    """
    Display detailed help information about the bot's commands and features.
    
    Usage: !help [command]
    Examples: !help, !help cite, !help reading_list
    """
    embed = discord.Embed(title="Research Assistant Bot Help", color=discord.Color.blue())
    
    if command is None:
        # General help overview
        embed.description = "This bot serves as a research assistant that can search for academic papers, manage citations, and help with research-related tasks."
        
        embed.add_field(
            name="📚 Standard Commands", 
            value=(
                "`!help` - Show this help message\n"
                "`!ping` - Check if the bot is responding\n"
                "`!papers` - List all papers that have been cited\n"
                "`!cite <number> <style>` - Format a citation\n"
                "`!bibliography <style>` - Show the bibliography\n"
                "`!citation_styles` - List available citation styles"
            ), 
            inline=False
        )
        
        embed.add_field(
            name="📝 Research Notes", 
            value=(
                "`!add_note <number> <text>` - Add a note to a paper\n"
                "`!view_notes [number]` - View notes for a paper/all papers\n"
                "`!delete_note <paper> <note>` - Delete a specific note\n"
                "`!clear_notes [number]` - Clear notes for a paper/all notes"
            ), 
            inline=False
        )
        
        embed.add_field(
            name="📋 Reading Lists", 
            value=(
                "`!reading_list create <name>` - Create a new reading list\n"
                "`!reading_list add <name> <paper>` - Add paper to list\n"
                "`!reading_list view [name]` - View a list or all lists\n"
                "`!reading_list remove <name> <paper>` - Remove paper from list\n"
                "`!reading_list delete <name>` - Delete a reading list"
            ), 
            inline=False
        )
        
        embed.add_field(
            name="🔍 Related Papers", 
            value="`!related <paper> [max_results]` - Find related papers", 
            inline=False
        )
        
        embed.add_field(
            name="💬 Natural Language Interactions", 
            value=(
                "You can also interact with the bot using natural language:\n"
                "• Ask research questions to search for papers\n"
                "• Request citations (e.g., 'cite paper 2 in MLA format')\n"
                "• Manage reading lists (e.g., 'create reading list called ML_Papers')\n"
                "• Find related papers (e.g., 'Get papers related to paper 2')\n"
                "\nFor more details on a specific command, type `!help <command>`"
            ), 
            inline=False
        )
        
    elif command.lower() == "cite":
        embed.title = "Help: Citation Command"
        embed.description = "Format a citation for a specific paper in the bibliography."
        embed.add_field(name="Usage", value="`!cite <paper_index> <style>`", inline=False)
        embed.add_field(name="Example", value="`!cite 1 apa`", inline=False)
        embed.add_field(name="Available Styles", value="APA, MLA, Chicago, Harvard, IEEE", inline=False)
        embed.add_field(
            name="Natural Language", 
            value="You can also use natural language: 'Can you cite paper 2 in MLA format?'", 
            inline=False
        )
        
    elif command.lower() == "bibliography":
        embed.title = "Help: Bibliography Command"
        embed.description = "Show the current bibliography in the specified format."
        embed.add_field(name="Usage", value="`!bibliography <style>`", inline=False)
        embed.add_field(name="Example", value="`!bibliography mla`", inline=False)
        embed.add_field(
            name="Natural Language", 
            value="You can also use natural language: 'Show me the bibliography in Harvard style'", 
            inline=False
        )
        
    elif command.lower() == "papers":
        embed.title = "Help: Papers Command"
        embed.description = "List all papers that have been cited in the conversation."
        embed.add_field(name="Usage", value="`!papers`", inline=False)
        embed.add_field(
            name="Natural Language", 
            value="You can also use natural language: 'Show me the papers you've cited'", 
            inline=False
        )
        
    elif command.lower() == "citation_styles":
        embed.title = "Help: Citation Styles Command"
        embed.description = "List all available citation styles."
        embed.add_field(name="Usage", value="`!citation_styles`", inline=False)
        embed.add_field(
            name="Natural Language", 
            value="You can also use natural language: 'What citation styles do you support?'", 
            inline=False
        )
        
    elif command.lower() == "add_note":
        embed.title = "Help: Add Note Command"
        embed.description = "Add a note to a specific paper."
        embed.add_field(name="Usage", value="`!add_note <paper_index> <note_text>`", inline=False)
        embed.add_field(name="Example", value="`!add_note 1 This paper has an interesting methodology.`", inline=False)
        embed.add_field(
            name="Natural Language", 
            value="You can also use natural language: 'Add note to paper 1: This paper has interesting methodology'", 
            inline=False
        )
        
    elif command.lower() == "view_notes":
        embed.title = "Help: View Notes Command"
        embed.description = "View notes for a specific paper or all papers."
        embed.add_field(name="Usage", value="`!view_notes [paper_index]`", inline=False)
        embed.add_field(name="Examples", value="`!view_notes 1` or `!view_notes`", inline=False)
        embed.add_field(
            name="Natural Language", 
            value="You can also use natural language: 'Show notes for paper 1' or 'View all my research notes'", 
            inline=False
        )
        
    elif command.lower() == "delete_note":
        embed.title = "Help: Delete Note Command"
        embed.description = "Delete a specific note from a paper."
        embed.add_field(name="Usage", value="`!delete_note <paper_index> <note_index>`", inline=False)
        embed.add_field(name="Example", value="`!delete_note 1 2`", inline=False)
        embed.add_field(
            name="Natural Language", 
            value="You can also use natural language: 'Delete note 2 from paper 1'", 
            inline=False
        )
        
    elif command.lower() == "clear_notes":
        embed.title = "Help: Clear Notes Command"
        embed.description = "Clear all notes for a specific paper or all papers."
        embed.add_field(name="Usage", value="`!clear_notes [paper_index]`", inline=False)
        embed.add_field(name="Examples", value="`!clear_notes 1` or `!clear_notes`", inline=False)
        embed.add_field(
            name="Natural Language", 
            value="You can also use natural language: 'Clear notes for paper 3' or 'Delete all my research notes'", 
            inline=False
        )
        
    elif command.lower() == "reading_list":
        embed.title = "Help: Reading List Command"
        embed.description = "Manage reading lists - create lists, add/remove papers, and view lists."
        embed.add_field(
            name="Usage", 
            value="`!reading_list <action> [name] [paper_index]`\nActions: create, add, view, remove, delete", 
            inline=False
        )
        embed.add_field(
            name="Examples", 
            value=(
                "`!reading_list create ML_Healthcare`\n"
                "`!reading_list add ML_Healthcare 3`\n"
                "`!reading_list view ML_Healthcare`\n"
                "`!reading_list view` (shows all lists)\n"
                "`!reading_list remove ML_Healthcare 2`\n"
                "`!reading_list delete ML_Healthcare`"
            ), 
            inline=False
        )
        embed.add_field(
            name="Natural Language", 
            value=(
                "You can also use natural language:\n"
                "• 'Create a reading list called Quantum_Computing'\n"
                "• 'Add paper 1 to reading list Quantum_Computing'\n"
                "• 'Display papers in my Quantum_Computing reading list'\n"
                "• 'Remove paper 1 from my Quantum_Computing reading list'\n"
                "• 'Delete my Quantum_Computing reading list'"
            ), 
            inline=False
        )
        
    elif command.lower() == "related":
        embed.title = "Help: Related Papers Command"
        embed.description = "Find papers related to a specific paper based on title, authors, and content."
        embed.add_field(name="Usage", value="`!related <paper_index> [max_results]`", inline=False)
        embed.add_field(name="Example", value="`!related 1 3`", inline=False)
        embed.add_field(
            name="Natural Language", 
            value="You can also use natural language: 'Get papers related to paper 2'",
            inline=False
        )
        
    else:
        embed.description = f"Command `{command}` not found. Use `!help` to see all available commands."
    
    await ctx.send(embed=embed)

bot.run(token)