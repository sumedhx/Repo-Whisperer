# backend/ingest/fetch_repo.py

import requests
from urllib.parse import urlparse

def parse_github_url(url):
    parsed = urlparse(url)
    parts = parsed.path.strip('/').split('/')
    return parts[0], parts[1]  # owner, repo

def list_repo_files(owner, repo, token=None, branch='main', extensions=('.py', '.js', '.jsx', '.ts', '.tsx', '.md', '.cpp', '.h')):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    try:
        print(f"📦 Fetching full tree: {url}")
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        data = res.json()
        
        # ✅ All files & folders (complete repo structure)
        repoTree = [item['path'] for item in data.get('tree', [])]

        # ✅ Filtered files by extension
        files = [
            item['path']
            for item in data.get('tree', [])
            if item['type'] == 'blob' and item['path'].endswith(extensions)
        ]

        print(f"✅ Total matched files: {len(files)}")
        print(files)
        print("Repo Tree: ", repoTree)
        return files, repoTree
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch repo tree: {e}")
        return []
