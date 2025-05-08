import os
import requests
import openai
import tempfile
import subprocess
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
import re
import argparse

GITHUB_API = "https://api.github.com"

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Instantiate OpenAI client (new API)
client = OpenAI()

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

CODE_EXTS = (
    '.py', '.js', '.ts', '.java', '.go', '.rb', '.cpp', '.c',
    '.cs', '.php', '.rs', '.swift', '.kt', '.scala', '.sh',
    '.pl', '.html', '.css'
)

def ensure_command(cmd):
    from shutil import which
    if which(cmd) is None:
        raise RuntimeError(f"Required command not found: {cmd}")

def list_repos(username: str) -> List[dict]:
    repos = []
    page = 1
    while True:
        url = f"{GITHUB_API}/user/repos?per_page=100&page={page}"
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return [repo for repo in repos if repo['owner']['login'].lower() == username.lower()]

def clone_repo(clone_url: str, dest: str) -> str:
    repo_name = clone_url.rstrip("/").rsplit("/", 1)[-1].replace(".git", "")
    target = os.path.join(dest, repo_name)
    subprocess.run(["git", "clone", "--depth", "1", clone_url, target], check=True)
    return target

def collect_code_snippets(repo_path: str, max_files=5, max_bytes=2048) -> str:
    code = []
    count = 0
    for root, dirs, files in os.walk(repo_path):
        for skip in ('node_modules', 'vendor', '__pycache__', '.git'):
            if skip in dirs:
                dirs.remove(skip)
        for file in files:
            if file.lower().endswith(CODE_EXTS):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        snippet = f.read(max_bytes)
                    code.append(f"# {file}\n{snippet}")
                    count += 1
                    if count >= max_files:
                        return '\n'.join(code)
                except Exception:
                    continue
    return '\n'.join(code)

def suggest_description_with_openai(code_snippet: str) -> str:
    prompt = (
        "Given the following code snippets from a GitHub repository, write a concise, clear, and informative GitHub repository description (max 140 characters). "
        "The description should summarize the repository's purpose and main functionality.\n\n"
        f"{code_snippet}"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80,
        temperature=0.4,
    )
    content = response.choices[0].message.content.strip()
    # Truncate to 140 chars if needed
    return content[:140]

def update_repo_description(owner: str, repo: str, description: str):
    url = f"{GITHUB_API}/repos/{owner}/{repo}"
    data = {"description": description}
    r = requests.patch(url, headers=HEADERS, json=data)
    r.raise_for_status()
    print(f"Updated description for {owner}/{repo}: {description}")

def main():
    parser = argparse.ArgumentParser(description="Auto-update GitHub repo descriptions with OpenAI.")
    parser.add_argument("--only-public", action="store_true", help="Only process public repositories (skip private repos)")
    parser.add_argument("--only-empty", action="store_true", help="Only process repositories with empty descriptions.")
    parser.add_argument("--skip-without-description", action="store_true", help="Skip repositories that do not have a description set.")
    args = parser.parse_args()

    ensure_command("git")
    repos = list_repos(GITHUB_USERNAME)
    print(f"Found {len(repos)} repos.")
    for repo in repos:
        name = repo['name']
        if repo.get('fork'):
            print(f" → Skipping forked repo: {name}")
            continue
        if args.only_public and repo.get('private', False):
            print(f" → Skipping private repo (only-public): {name}")
            continue
        if args.only_empty and repo.get('description'):
            print(f" → Skipping repo with description (only-empty): {name}")
            continue
        if args.skip_without_description and not repo.get('description'):
            print(f" → Skipping repo without description (skip-without-description): {name}")
            continue
        print(f"\nProcessing {name}...")
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                clone_url = repo['clone_url'].replace(
                    'https://', f'https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@')
                repo_dir = clone_repo(clone_url, tmpdir)
                code = collect_code_snippets(repo_dir)
                if not code:
                    print(" → No code found; skipping.")
                    continue
                description = suggest_description_with_openai(code)
                if description:
                    update_repo_description(GITHUB_USERNAME, name, description)
                else:
                    print(" → No valid description to update.")
            except subprocess.CalledProcessError as e:
                print(f" → Git error cloning {name}: {e}")
            except requests.HTTPError as e:
                print(f" → GitHub API error on {name}: {e}")
                print(f" → Response: {e.response.text}")
            except Exception as e:
                print(f" → Unexpected error on {name}: {e}")

if __name__ == "__main__":
    main() 