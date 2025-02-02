import requests
from app.config import GITHUB_API_URL, GITHUB_TOKEN

async def search_github_repositories(query: str):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        response = requests.get(
            GITHUB_API_URL,
            params={
                'q': f"{query}",
                'sort': 'stars',
                'order': 'desc',
                'per_page': 5
            },
            headers=headers
        )
        response.raise_for_status()
    except requests.HTTPError as e:
        print(f"GitHub API request failed: {e}")
        return []
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return []

    data = response.json()
    items = data.get('items', [])
    repositories = []

    for item in items:
        repo_name = item['name']
        repo_url = item['html_url']
        owner_avatar_url = item['owner']['avatar_url']  # Get the avatar URL of the repository owner
        
        repositories.append({
            'name': repo_name,
            'html_url': repo_url,
            'thumbnail_url': owner_avatar_url  # Add the thumbnail URL to the results
        })

    print(repositories)  # Print the results for debugging
    return repositories
