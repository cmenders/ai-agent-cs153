import asyncio
import aiohttp
import re
from scholarly import scholarly

async def search_google_scholar(query: str, maxResults: int = 3):
    """
    Search for academic papers, prioritizing the Semantic Scholar API.
    If that fails, attempt to use Google Scholar via the scholarly library as a fallback.
    """
    try:
        # Try semantic search first (previously the fallback method)
        results = await semantic_scholar_search(query, maxResults)
        
        # If we got results, return them
        if results:
            return results
            
        # Otherwise, try scholarly as a fallback
        print(f"Semantic Scholar search returned no results for '{query}', trying scholarly")
        return await scholarly_search(query, maxResults)
    except Exception as e:
        print(f"Error in semantic search: {e}, trying scholarly as fallback")
        return await scholarly_search(query, maxResults)

async def scholarly_search(query: str, maxResults: int = 3):
    """Attempt to search using Google Scholar via scholarly"""
    try:
        # Set a strict timeout to prevent blocking
        return await asyncio.wait_for(
            asyncio.to_thread(_sync_search_google_scholar, query, maxResults),
            timeout=10.0  # 10-second timeout
        )
    except (asyncio.TimeoutError, Exception) as e:
        print(f"Error/timeout in scholarly search: {e}")
        return []  # Return empty list instead of dummy data

def _sync_search_google_scholar(query: str, maxResults: int = 3):
    """Synchronous version with reduced results"""
    try:
        results = []
        search_query = scholarly.search_pubs(query)
        
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
    except Exception as e:
        print(f"Error in _sync_search: {e}")
        return []

async def semantic_scholar_search(query: str, maxResults: int = 3):
    """Primary search method using Semantic Scholar API"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={maxResults}&fields=title,authors,year,citationCount,url",
                timeout=10
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    for paper in data.get("data", [])[:maxResults]:
                        results.append({
                            "title": paper.get("title", "Unknown Title"),
                            "authors": ", ".join([author.get("name", "") for author in paper.get("authors", [])[:3]]),
                            "year": paper.get("year", "Unknown"),
                            "citations": paper.get("citationCount", 0),
                            "url": paper.get("url", "No URL available")
                        })
                    
                    return results
    except Exception as e:
        print(f"Semantic Scholar search error: {e}")
    
    return []  # Return empty list instead of dummy data

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