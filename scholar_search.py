import asyncio
import aiohttp
import re
from scholarly import scholarly

async def search_google_scholar(query: str, maxResults: int = 3):
    try:
        # Set a strict timeout to prevent blocking
        results = await asyncio.wait_for(
            asyncio.to_thread(_sync_search_google_scholar, query, maxResults),
            timeout=10.0  # 10-second timeout
        )
        
        # If we got results, return them
        if results:
            return results
            
        # Otherwise, try the fallback method
        return await fallback_search(query, maxResults)
    except (asyncio.TimeoutError, Exception) as e:
        print(f"Error/timeout in scholarly search: {e}, trying fallback")
        return await fallback_search(query, maxResults)

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

async def fallback_search(query: str, maxResults: int = 3):
    """Simplified fallback search that won't block"""
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
        print(f"Fallback search error: {e}")
    
    # Return dummy data as last resort to prevent bot from breaking
    return [
        {
            "title": f"Search result for: {query} (Error retrieving papers)",
            "authors": "Search service temporarily unavailable",
            "year": "2023",
            "citations": 0,
            "url": "https://scholar.google.com/scholar?q=" + query.replace(" ", "+")
        }
    ]

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