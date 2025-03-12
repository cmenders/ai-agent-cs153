import asyncio
from scholarly import scholarly

async def search_google_scholar(query: str, maxResults: int = 3):
    try:
        # Run the synchronous scholarly code in a separate thread
        return await asyncio.to_thread(_sync_search_google_scholar, query, maxResults)
    except Exception as e:
        print(f"Error searching Google Scholar: {e}")
        return []

def _sync_search_google_scholar(query: str, maxResults: int = 3):
    """Synchronous version that runs in a separate thread"""
    try:
        search_query = scholarly.search_pubs(query)
        results = []
        for i in range(maxResults):
            try:
                publication = next(search_query)
                paper_info = {
                    "title": publication.get("bib", {}).get("title", "Unknown Title"),
                    "authors": publication.get("bib", {}).get("author", "Unknown Authors"),
                    "year": publication.get("bib", {}).get("pub_year", "Unknown Year"),
                    "citations": publication.get("num_citations", 0),
                    "url": publication.get("pub_url", "No URL available")
                }
                results.append(paper_info)
            except StopIteration:
                break
            except Exception:
                continue
        return results
    except Exception:
        return []

async def format_search_results(searchQ: str, results: list) -> str:
    if not results:
        return f"0 results found for '{searchQ}'."
    
    formatted_results = ""
    for i, paper in enumerate(results, 1):
        formatted_results += f"Paper {i}:\n"
        formatted_results += f"Title: {paper['title']}\n"
        formatted_results += f"Authors: {paper['authors']}\n"
        formatted_results += f"Year: {paper['year']}\n"
        formatted_results += f"Citations: {paper['citations']}\n"
        formatted_results += f"URL: {paper['url']}\n\n"
    
    return formatted_results 