class Bibliography:
    def __init__(self):
        self.cited_papers = {}

    def add_paper(self, paper):
        key = f"{paper['title']}_{paper['year']}"
        if key not in self.cited_papers:
            self.cited_papers[key] = paper

    def get_formatted_bibliography(self):
        if not self.cited_papers:
            return "No papers have been cited in this conversation."

        formatted_bib = "Bibliography:\n\n"
        for i, paper in enumerate(self.cited_papers.values(), 1):
            formatted_bib += f"{i}. {paper['authors']} ({paper['year']}). {paper['title']}. "
            formatted_bib += f"Citations: {paper['citations']}. "
            formatted_bib += f"URL: {paper['url']}\n\n"
        return formatted_bib