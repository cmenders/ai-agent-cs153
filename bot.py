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
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

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

bot.run(token)