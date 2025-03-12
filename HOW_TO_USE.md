**# Research Assistant Discord Bot

## Overview
This Discord bot serves as a research assistant that can search Google Scholar, find academic papers, and help users with research-related questions. The bot uses Mistral AI to process queries and generate helpful responses based on scholarly research.

## Features
- **Research Paper Search**: Search for academic papers on Google Scholar
- **Paper Summarization**: Summarize key findings from papers
- **Bibliography Management**: Keep track of papers cited in a conversation
- **Citation Formatting**: Format citations in various academic styles
- **Research Notes**: Add, view, and manage notes for papers
- **Reading Lists**: Organize papers into custom collections for different research topics
- **Related Papers Recommendation**: Get suggestions for papers related to your current reading

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
| `!reading_list create <name>` | Create a new reading list | `!reading_list create ML_Healthcare` |
| `!reading_list add <name> <paper_number>` | Add paper to a reading list | `!reading_list add ML_Healthcare 3` |
| `!reading_list view [name]` | View a specific or all reading lists | `!reading_list view ML_Healthcare` |
| `!reading_list remove <name> <paper_number>` | Remove paper from a reading list | `!reading_list remove ML_Healthcare 3` |
| `!reading_list delete <name>` | Delete an entire reading list | `!reading_list delete ML_Healthcare` |
| `!related <paper_number> [max_results]` | Find papers related to the specified paper | `!related 2 5` |

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
```

#### Bibliography Management

Access the bibliography with natural language:
```
Show me the bibliography in Harvard style
```

#### Paper Listing

Get a list of papers:
```
Show me the papers you've cited
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

#### Reading Lists

Create and manage reading lists:
```
Create a reading list called Quantum_Computing
Display papers in my Quantum_Computing reading list
Remove paper 1 from my Quantum_Computing reading list
Delete my Quantum_Computing reading list
```

#### Related Papers

Find papers related to your current readings based on title, authors, and abstract similarity:
```
Find papers related to paper 1
Get papers related to paper 2
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

### Example 5: Reading Lists

User:
```
Create a reading list called Quantum_Computing
```

Bot:
```
✓ Created reading list: Quantum_Computing
```

User:
```
add paper 1 to reading list Quantum_Computing
```

Bot:
```
✓ Added paper "Advances in Quantum Computing Algorithms" to reading list: Quantum_Computing
```

### Example 6: Related Papers

User:
```
Find papers related to paper 1
```

Bot:
```
Papers related to "Advances in Quantum Computing Algorithms":

1. "Quantum Supremacy and Its Applications" (2024)
   Similarity: 87%
   • Shared authors: J. Smith
   • Similar research focus on quantum algorithms
   • Builds on error correction methods from the original paper

2. "Practical Implementations of NISQ Algorithms" (2023)
   Similarity: 76%
   • Different authors but cites the original paper extensively
   • Focuses on practical applications of the theoretical work
   • Uses the same experimental framework

3. "Survey of Quantum Error Correction Methods" (2022)
   Similarity: 73%
   • Different authors
   • Covers the same error correction approach in detail
   • Cites similar foundational papers
```**