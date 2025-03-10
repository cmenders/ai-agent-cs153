from citation_formatter import format_citation, get_available_styles

class Bibliography:
    def __init__(self):
        self.cited_papers = {}

    def add_paper(self, paper):
        key = f"{paper['title']}_{paper['year']}"
        if key not in self.cited_papers:
            self.cited_papers[key] = paper
        return key  # Return the paper key for use with notes

    def get_formatted_bibliography(self, style="apa"):
        """
        Get the bibliography formatted in the specified citation style
        
        Parameters:
        style (str): Citation style (apa, mla, chicago, harvard, ieee)
        
        Returns:
        str: Formatted bibliography
        """
        if not self.cited_papers:
            return "No papers have been cited in this conversation."

        style = style.lower()
        formatted_bib = f"Bibliography ({style.upper()} format):\n\n"
        
        for i, paper in enumerate(self.cited_papers.values(), 1):
            formatted_bib += f"{i}. {format_citation(paper, style)}\n\n"
        
        return formatted_bib
    
    def get_citation(self, paper_index, style="apa"):
        """
        Get a specific citation formatted in the requested style
        
        Parameters:
        paper_index (int): Index of the paper in the bibliography (1-based)
        style (str): Citation style (apa, mla, chicago, harvard, ieee)
        
        Returns:
        str: Formatted citation or error message
        """
        papers = list(self.cited_papers.values())
        
        if not papers:
            return "No papers have been cited in this conversation."
        
        try:
            paper_index = int(paper_index)
            if paper_index < 1 or paper_index > len(papers):
                return f"Invalid paper index. Valid range is 1-{len(papers)}."
            
            paper = papers[paper_index - 1]
            return format_citation(paper, style)
        
        except ValueError:
            return "Invalid paper index. Please provide a number."
    
    def get_paper_list(self):
        """
        Get a simple list of papers with their indices
        
        Returns:
        str: Formatted list of papers
        """
        if not self.cited_papers:
            return "No papers have been cited in this conversation."
            
        formatted_list = "Cited Papers:\n\n"
        for i, paper in enumerate(self.cited_papers.values(), 1):
            formatted_list += f"{i}. {paper['title']} ({paper['year']})\n"
        
        return formatted_list
    
    def get_paper_by_index(self, paper_index):
        """
        Get a paper by its index in the bibliography
        
        Parameters:
        paper_index (int): Index of the paper (1-based)
        
        Returns:
        tuple: (paper_key, paper_dict) if found, (None, None) otherwise
        """
        try:
            paper_index = int(paper_index)
            papers = list(self.cited_papers.items())
            
            if 1 <= paper_index <= len(papers):
                return papers[paper_index - 1]
            
            return None, None
        except (ValueError, IndexError):
            return None, None
    
    def get_paper_info_dict(self):
        """
        Get a dictionary of paper keys to paper info
        
        Returns:
        dict: Dictionary mapping paper keys to paper information
        """
        return self.cited_papers
    
    def get_paper_title(self, paper_key):
        """
        Get the title of a paper by its key
        
        Parameters:
        paper_key (str): The key of the paper
        
        Returns:
        str: The title of the paper, or None if not found
        """
        if paper_key in self.cited_papers:
            return f"{self.cited_papers[paper_key]['title']} ({self.cited_papers[paper_key]['year']})"
        return None