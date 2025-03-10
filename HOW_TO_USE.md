# Research Assistant Discord Bot

## Overview
This Discord bot serves as a research assistant that can search Google Scholar, find academic papers, and help users with research-related questions. The bot uses Mistral AI to process queries and generate helpful responses based on scholarly research.

## Features
- **Research Paper Search**: Search for academic papers on Google Scholar
- **Paper Summarization**: Summarize key findings from papers
- **Bibliography Management**: Keep track of papers cited in a conversation
- **Citation Formatting**: Format citations in various academic styles
- **Research Notes**: Add, view, and manage notes for papers

## Commands

### Standard Commands (with prefix `!`)

| Command | Description | Example |
|---------|-------------|---------|
| `!ping` | Check if the bot is responding | `!ping` |
| `!cite <number> <style>` | Format a specific paper in a citation style | `!cite 1 apa` |
| `!bibliography <style>` | Show the bibliography in a specific format | `!bibliography mla` |
| `!papers` | List all papers that have been cited | `!papers` |
| `!citation_styles` | List all available citation styles | `!citation_styles` |
| `!add_note <number> <text>` | Add a note to a specific paper | `!add_note 1 Interesting methodology` |
| `!view_notes [number]` | View notes for a paper or all papers | `!view_notes 1` or `!view_notes` |
| `!delete_note <paper> <note>` | Delete a specific note | `!delete_note 1 2` |
| `!clear_notes [number]` | Clear notes for a paper or all notes | `!clear_notes 1` or `!clear_notes` |

### Natural Language Interactions

The bot also responds to natural language requests, without needing a command prefix:

#### Research Queries
Simply ask a research question, and the bot will search for relevant papers:
```
What are the recent advances in machine learning for healthcare?
```

#### Citation Formatting

Request citations using natural language:
```
Can you cite paper 2 in MLA format?
Format the third paper in Chicago style
Give me an IEEE citation for paper 1
```

#### Bibliography Management

Access the bibliography with natural language:
```
Show me the bibliography in Harvard style
List all the references
Display the citations in APA format
```

#### Paper Listing

Get a list of papers:
```
List all the papers you've found
Show me the papers you've cited
What papers do you have?
```

#### Research Notes

Add notes to papers:
```
Add note to paper 1: This paper has interesting methodology
Create a note for paper 2: Need to follow up on this author's other work
```

View notes:
```
Show notes for paper 1
View all my research notes
Display notes on paper 3
```

Delete or clear notes:
```
Delete note 2 from paper 1
Clear notes for paper 3
Delete all my research notes
```

#### Citation Styles

Ask about available citation styles:
```
What citation styles do you support?
Which citation formats are available?
```

## Available Citation Styles

The bot supports the following citation styles:
- **APA** (American Psychological Association, 7th edition)
- **MLA** (Modern Language Association, 8th edition)
- **Chicago** (17th edition)
- **Harvard**
- **IEEE** (Institute of Electrical and Electronics Engineers)

## Example Interactions

### Example 1: Research Query

User:
```
Tell me about recent research on quantum computing algorithms
```

Bot:
```
Searching for: 'quantum computing algorithms recent research'...

Based on the papers I found, recent research in quantum computing algorithms has been making significant progress in several areas:

[Summary of findings from papers]

I've added these papers to the bibliography. You can view them by typing "show bibliography" or get specific citations with "cite paper 1 in APA".
```

### Example 2: Citation Formatting

User:
```
Cite paper 2 in Chicago style
```

Bot:
```
John Smith and Jane Doe. "Advances in Quantum Computing Algorithms." 2023. https://example.com/paper.
```

### Example 3: Bibliography Request

User:
```
Show bibliography in MLA format
```

Bot:
```
Bibliography (MLA format):

1. Smith et al. "Advances in Quantum Computing Algorithms." 2023. Web. Accessed 10 Mar. 2025. https://example.com/paper1

2. Doe, Jane and John Smith. "Quantum Supremacy Applications." 2024. Web. Accessed 10 Mar. 2025. https://example.com/paper2

3. [Additional papers...]
```

### Example 4: Research Notes

User:
```
Add note to paper 1: This paper presents a novel approach to quantum error correction that could be applicable to our research.
```

Bot:
```
✓ Note added to paper: Advances in Quantum Computing Algorithms (2023)
```

User:
```
Show notes for paper 1
```

Bot:
```
Research Notes:

Paper: Advances in Quantum Computing Algorithms (2023)
  Note 1 [2025-03-10 14:32:45]:
  This paper presents a novel approach to quantum error correction that could be applicable to our research.
```