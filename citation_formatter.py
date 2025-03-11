"""
Functions for formatting citations in different styles (APA, MLA, Chicago, etc.)
"""

def format_apa(paper):
    """
    Format a paper citation in APA style (7th edition)
    """
    authors = format_apa_authors(paper['authors'])
    title = paper['title']
    year = paper['year']
    url = paper['url']
    
    citation = f"{authors} ({year}). {title}. Retrieved from {url}"
    return citation

def format_mla(paper):
    """
    Format a paper citation in MLA style (8th edition)
    """
    authors = format_mla_authors(paper['authors'])
    title = f'"{paper["title"]}."'
    year = paper['year']
    url = paper['url']
    
    citation = f"{authors}. {title} {year}. Web. Accessed {get_today_formatted()}. {url}"
    return citation

def format_chicago(paper):
    """
    Format a paper citation in Chicago style (17th edition)
    """
    authors = format_chicago_authors(paper['authors'])
    title = f'"{paper["title"]}."'
    year = paper['year']
    url = paper['url']
    
    citation = f"{authors}. {title} {year}. {url}."
    return citation

def format_harvard(paper):
    """
    Format a paper citation in Harvard style
    """
    authors = format_harvard_authors(paper['authors'])
    title = paper['title']
    year = paper['year']
    url = paper['url']
    
    citation = f"{authors} ({year}). {title}. Available at: {url} (Accessed: {get_today_formatted_harvard()})."
    return citation

def format_ieee(paper):
    """
    Format a paper citation in IEEE style
    """
    authors = format_ieee_authors(paper['authors'])
    title = f'"{paper["title"]},"'
    year = paper['year']
    
    citation = f"{authors}, {title} {year}. [Online]. Available: {paper['url']}"
    return citation

# Helper functions for author formatting
def format_apa_authors(authors):
    """Format authors in APA style"""
    if isinstance(authors, str):
        # If we have a string of authors, try to split and format
        author_list = authors.split(", ")
        if len(author_list) == 1:
            return authors
        elif len(author_list) == 2:
            return f"{author_list[0]} & {author_list[1]}"
        else:
            return f"{', '.join(author_list[:-1])}, & {author_list[-1]}"
    return authors

def format_mla_authors(authors):
    """Format authors in MLA style"""
    if isinstance(authors, str):
        author_list = authors.split(", ")
        if len(author_list) == 1:
            return authors
        elif len(author_list) > 1:
            # MLA uses first author's last name, then "et al." for 3+ authors
            if len(author_list) > 2:
                return f"{author_list[0]} et al"
            else:
                return f"{author_list[0]} and {author_list[1]}"
    return authors

def format_chicago_authors(authors):
    """Format authors in Chicago style"""
    if isinstance(authors, str):
        author_list = authors.split(", ")
        if len(author_list) == 1:
            return authors
        elif len(author_list) == 2:
            return f"{author_list[0]} and {author_list[1]}"
        else:
            # Chicago uses all authors
            return f"{', '.join(author_list[:-1])}, and {author_list[-1]}"
    return authors

def format_harvard_authors(authors):
    """Format authors in Harvard style"""
    if isinstance(authors, str):
        author_list = authors.split(", ")
        if len(author_list) == 1:
            return authors
        elif len(author_list) == 2:
            return f"{author_list[0]} and {author_list[1]}"
        else:
            # Harvard uses "et al." for 4+ authors, otherwise all authors
            if len(author_list) > 3:
                return f"{author_list[0]} et al."
            else:
                return f"{', '.join(author_list[:-1])} and {author_list[-1]}"
    return authors

def format_ieee_authors(authors):
    """Format authors in IEEE style"""
    if isinstance(authors, str):
        author_list = authors.split(", ")
        if len(author_list) == 1:
            return authors
        elif len(author_list) > 1:
            # IEEE uses first initial followed by last name
            # For simplicity, we'll just use the provided names as-is
            return f"{', '.join(author_list)}"
    return authors

# Helper function to get today's date formatted for citations
def get_today_formatted():
    """Get today's date formatted as DD Month YYYY for MLA citations"""
    from datetime import datetime
    return datetime.now().strftime("%d %b. %Y")

def get_today_formatted_harvard():
    """Get today's date formatted as DD Month YYYY for Harvard citations"""
    from datetime import datetime
    return datetime.now().strftime("%d %B %Y")

# Main function to format a citation in the requested style
def format_citation(paper, style="apa"):
    """
    Format a citation in the requested style
    
    Parameters:
    paper (dict): Paper information with keys: title, authors, year, url
    style (str): Citation style ("apa", "mla", "chicago", "harvard", "ieee")
    
    Returns:
    str: Formatted citation
    """
    style = style.lower()
    
    if style == "apa":
        return format_apa(paper)
    elif style == "mla":
        return format_mla(paper)
    elif style == "chicago":
        return format_chicago(paper)
    elif style == "harvard":
        return format_harvard(paper)
    elif style == "ieee":
        return format_ieee(paper)
    else:
        # Default to APA if style not recognized
        return format_apa(paper)

# Get all available citation styles
def get_available_styles():
    """Return a list of all available citation styles"""
    return ["apa", "mla", "chicago", "harvard", "ieee"]