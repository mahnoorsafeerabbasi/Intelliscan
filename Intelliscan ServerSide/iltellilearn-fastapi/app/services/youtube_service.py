import requests
import httpx
from app.config import YOUTUBE_SEARCH_URL, GOOGLE_API_KEY

async def search_youtube_videos(query: str):
    params = {
        'part': 'snippet',
        'q': f"{query} programming OR coding OR tutorial",
        'type': 'video',
        'maxResults': 5,
        'key': GOOGLE_API_KEY
    }
    try:
        response = await httpx.AsyncClient().get(YOUTUBE_SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()
        items = data.get('items', [])
        # Extract thumbnail URL from each video item
        return [{
            'title': item['snippet']['title'],
            'video_url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            'thumbnail_url': item['snippet']['thumbnails'].get('high', {}).get('url', '')
        } for item in items]
    except httpx.HTTPStatusError as e:
        print(f"YouTube API request failed: {e}")
        return []
    except httpx.RequestError as e:
        print(f"Request error: {e}")
        return []
