# Auto Update GitHub Repo Descriptions

This script automatically reviews the code in all your GitHub repositories and updates their **descriptions** using OpenAI. It clones each repository, samples code files, and generates a concise, informative description for each repo using GPT-4o. The new description is then updated on GitHub via the API.

## Features

- Authenticates with GitHub and OpenAI
- Clones all your (non-fork) repositories
- Samples code from each repo to generate a description
- Uses OpenAI GPT-4o to summarize the repository's purpose
- Updates the description for each repo via the GitHub API
- Options to process only public repos, only those with empty descriptions, or to skip repos without a description
- Skips forked repositories by default

## Setup

### 1. Clone this repository or copy the script files

### 2. Create a `.env` file in the `update-repository-descriptions` directory:

```ini
GITHUB_USERNAME=your_github_username
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=your_openai_api_key
```
- **GITHUB_TOKEN**: Needs `repo` scope for private repos and description editing.
- **OPENAI_API_KEY**: Needs access to GPT-4 or GPT-4o.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Test the connections (optional but recommended)

```bash
python test_connection.py
```

This will verify that your API keys are working correctly.

### 5. Run the script

```bash
python update_repo_description.py [--only-public] [--only-empty] [--skip-without-description]
```
- `--only-public`: Only process public repositories (skip private repos)
- `--only-empty`: Only process repositories that have no description set
- `--skip-without-description`: Skip repositories that do not have a description set
- You can use these flags together to fine-tune which repositories are processed

## How it Works
- The script lists all repositories for your GitHub user.
- For each repo, it clones the code (shallow clone), samples up to 5 code files, and sends snippets to OpenAI's GPT-4o model.
- The model returns a concise description (max 140 characters), which is then set as the new repository description via the GitHub API.
- Forked repositories are skipped.
- If `--only-public` is set, private repos are skipped.
- If `--only-empty` is set, repos with a description are skipped.
- If `--skip-without-description` is set, repos without a description are skipped.

## Files
- `update_repo_description.py`: Main script
- `test_connection.py`: Test script to verify API connections
- `requirements.txt`: Python dependencies
- `.gitignore`: Ignores Python, environment, and secret files
- `.env` (not committed): Your credentials (see above)

## Troubleshooting
- **Permission errors:** Ensure your GitHub token has the `repo` scope.
- **API errors:** Check your API keys and rate limits for both GitHub and OpenAI.
- **No code found:** The script only samples certain file types; empty or non-code repos will be skipped.
- **OpenAI cost:** Each repo analysis sends code to OpenAI. Monitor your usage and costs.

## Security
- Never share your `.env` file or API keys.
- The script embeds your GitHub token in the clone URL for non-interactive cloning.

## License
MIT