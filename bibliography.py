from citation_formatter import format_citation, get_available_styles
import re
from collections import Counter

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
        
    def find_related_papers(self, paper_index, max_results=5):
        """
        Find papers related to the specified paper based on title, authors, and abstract similarity
        
        Parameters:
        paper_index (int): Index of the paper to find related papers for (1-based)
        max_results (int): Maximum number of related papers to return
        
        Returns:
        list: List of related papers with similarity scores
        """
        paper_key, target_paper = self.get_paper_by_index(paper_index)
        if not paper_key:
            return f"Paper {paper_index} not found. Use 'list papers' to see available papers."
            
        papers = list(self.cited_papers.items())
        if len(papers) <= 1:
            return "Not enough papers in the bibliography to find related papers."
            
        # Calculate similarity scores between target paper and all other papers
        related_papers = []
        
        for key, paper in papers:
            if key == paper_key:  # Skip the target paper
                continue
                
            similarity_score = self._calculate_similarity(target_paper, paper)
            related_papers.append({
                "key": key,
                "paper": paper,
                "similarity_score": similarity_score
            })
            
        # Sort by similarity score (higher is more related)
        related_papers.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # Format the results
        if not related_papers:
            return "No related papers found."
            
        formatted_result = f"Papers related to '{target_paper['title']}':\n\n"
        
        for i, paper_data in enumerate(related_papers[:max_results], 1):
            paper = paper_data["paper"]
            score = paper_data["similarity_score"]
            formatted_result += f"{i}. {paper['title']} ({paper['year']})\n"
            formatted_result += f"   Authors: {', '.join(paper.get('authors', ['Unknown']))}\n"
            formatted_result += f"   Similarity: {score:.2f}\n"
            formatted_result += f"   Reason: {self._explain_similarity(target_paper, paper)}\n\n"
            
        return formatted_result
    
    def _calculate_similarity(self, paper1, paper2):
        """
        Calculate a similarity score between two papers
        
        Parameters:
        paper1 (dict): First paper
        paper2 (dict): Second paper
        
        Returns:
        float: Similarity score (0-1, higher means more similar)
        """
        score = 0.0
        
        # Check for common authors (highest weight)
        authors1 = set(author.lower() for author in paper1.get('authors', []))
        authors2 = set(author.lower() for author in paper2.get('authors', []))
        
        if authors1 and authors2:  # Only if both have authors
            common_authors = authors1.intersection(authors2)
            if common_authors:
                score += 0.4 * (len(common_authors) / max(len(authors1), len(authors2)))
        
        # Check for similar titles
        title1_words = self._tokenize_text(paper1.get('title', ''))
        title2_words = self._tokenize_text(paper2.get('title', ''))
        
        if title1_words and title2_words:
            common_words = set(title1_words).intersection(set(title2_words))
            title_similarity = len(common_words) / max(len(title1_words), len(title2_words))
            score += 0.3 * title_similarity
        
        # Check for similar abstracts/snippets
        abstract1 = paper1.get('abstract', paper1.get('snippet', ''))
        abstract2 = paper2.get('abstract', paper2.get('snippet', ''))
        
        if abstract1 and abstract2:
            abstract1_words = self._tokenize_text(abstract1)
            abstract2_words = self._tokenize_text(abstract2)
            
            common_words = set(abstract1_words).intersection(set(abstract2_words))
            abstract_similarity = len(common_words) / max(len(abstract1_words), len(abstract2_words))
            score += 0.2 * abstract_similarity
        
        # Check if they're in the same year (small boost)
        if paper1.get('year') == paper2.get('year'):
            score += 0.1
            
        return score
    
    def _tokenize_text(self, text):
        """
        Tokenize text and remove common stop words
        
        Parameters:
        text (str): Text to tokenize
        
        Returns:
        list: List of significant words
        """
        if not text:
            return []
            
        # Convert to lowercase and split by non-alphanumeric characters
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                      'of', 'in', 'to', 'for', 'with', 'on', 'at', 'from', 'by', 'about', 
                      'as', 'into', 'like', 'through', 'after', 'over', 'between', 'out', 
                      'against', 'during', 'without', 'before', 'under', 'around', 'among'}
        
        return [word for word in words if word not in stop_words and len(word) > 2]
    
    def _explain_similarity(self, paper1, paper2):
        """
        Generate an explanation for why two papers are similar
        
        Parameters:
        paper1 (dict): First paper
        paper2 (dict): Second paper
        
        Returns:
        str: Explanation of similarity
        """
        reasons = []
        
        # Check for common authors
        authors1 = set(author.lower() for author in paper1.get('authors', []))
        authors2 = set(author.lower() for author in paper2.get('authors', []))
        common_authors = authors1.intersection(authors2)
        
        if common_authors:
            authors_str = ', '.join(common_authors)
            reasons.append(f"Shares author(s): {authors_str}")
        
        # Check for similar titles
        title1_words = self._tokenize_text(paper1.get('title', ''))
        title2_words = self._tokenize_text(paper2.get('title', ''))
        common_title_words = Counter([w for w in title1_words if w in title2_words])
        
        if common_title_words:
            top_words = [word for word, _ in common_title_words.most_common(3)]
            if top_words:
                reasons.append(f"Similar topic keywords: {', '.join(top_words)}")
        
        # Check if they're from the same year
        if paper1.get('year') == paper2.get('year'):
            reasons.append(f"Published in the same year ({paper1.get('year')})")
        
        # If no specific reasons found, give a generic response
        if not reasons:
            reasons.append("Related based on content similarity")
        
        return '; '.join(reasons)