from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from app.services.github_service import search_github_repositories
from app.services.youtube_service import search_youtube_videos
from app.services.gemini_service import check_query_relevance_with_gemini
from app.config import GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID, GOOGLE_SEARCH_URL
import httpx

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def get_form():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Topic Search</title>
        </head>
        <body>
            <h1>Topic Search</h1>
            <form action="/search" method="post">
                <label for="query">Search Topic</label>
                <input type="text" id="query" name="query" required>
                <input type="submit" value="Search">
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.post("/search", response_class=HTMLResponse)
async def search(request: Request, query: str = Form(...)):
    # Check if the query is relevant using Gemini model
    is_relevant = await check_query_relevance_with_gemini(query)
    if not is_relevant:
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Search Results</title>
            </head>
            <body>
                <h1>Search Results for {query}</h1>
                <p>The search query is not relevant to computer science topics.</p>
            </body>
        </html>
        """)

    search_query = f"{query} code OR snippet OR example OR tutorial -stackoverflow.com"  # Refined search query
    
    async with httpx.AsyncClient() as client:
        try:
            # Search Google Custom Search for web results
            response = await client.get(
                GOOGLE_SEARCH_URL,
                params={
                    'key': GOOGLE_API_KEY,
                    'cx': GOOGLE_SEARCH_ENGINE_ID,
                    'q': search_query,
                    'num': 5  # Limit the number of search results
                }
            )
            response.raise_for_status()
            data = response.json()
            results = data.get('items', [])

            # Search GitHub for repositories related to the topic (no language filter)
            github_results = await search_github_repositories(query)

            # Search YouTube for videos related to the topic
            youtube_results = await search_youtube_videos(query)

            # Generate HTML for search results
            results_html = generate_results_html(github_results, youtube_results, results)

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Error fetching search results")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail="Error connecting to search service")
        except Exception as e:
            raise HTTPException(status_code=500, detail="An unexpected error occurred")

    html_content = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Search Results</title>
        </head>
        <body>
            <h1>Search Results for {query}</h1>
            {results_html}
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

def generate_results_html(github_results, youtube_results, results):
    results_html = "<h1>Search Results</h1>"
    
    if github_results:
        results_html += "<h2>GitHub Repositories</h2>"
        for item in github_results:
            name = item.get('name', 'No Name')
            url = item.get('html_url', '#')
            owner_avatar_url = item.get('owner', {}).get('avatar_url', '')
            results_html += f"""
            <div>
                {f'<img src="{owner_avatar_url}" alt="{name}" class="thumbnail">' if owner_avatar_url else ''}
                <h2><a href="{url}">{name}</a></h2>
            </div>
            """
    
    if youtube_results:
        results_html += "<h2>YouTube Videos</h2>"
        for item in youtube_results:
            title = item.get('title', 'No Title')
            video_url = item.get('video_url', '#')
            thumbnail_url = item.get('thumbnail_url', '')
            results_html += f"""
            <div>
                {f'<img src="{thumbnail_url}" alt="{title}" class="thumbnail">' if thumbnail_url else ''}
                <h2><a href="{video_url}">{title}</a></h2>
            </div>
            """
    
    if results:
        results_html += "<h2>Web Results</h2>"
        for item in results:
            title = item.get('title', 'No Title')
            link = item.get('link', '#')
            snippet = item.get('snippet', 'No Description')
            image_url = item.get('pagemap', {}).get('cse_image', [{}])[0].get('src', '')
            results_html += f"""
            <div>
                {f'<img src="{image_url}" alt="{title}" class="thumbnail">' if image_url else ''}
                <h2><a href="{link}">{title}</a></h2>
                <p>{snippet}</p>
            </div>
            """
    
    return results_html
