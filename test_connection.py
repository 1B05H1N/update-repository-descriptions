#!/usr/bin/env python3
"""
Simple test script to verify API connections are working.
"""

import os
from dotenv import load_dotenv
import requests
from openai import OpenAI

# Load environment variables
load_dotenv()

def test_github_connection():
    """Test GitHub API connection."""
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ GITHUB_TOKEN not found in environment")
        return False
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get("https://api.github.com/user", headers=headers)
        response.raise_for_status()
        user_data = response.json()
        print(f"✅ GitHub connection successful - logged in as: {user_data['login']}")
        return True
    except Exception as e:
        print(f"❌ GitHub connection failed: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connection."""
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False
    
    try:
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print("✅ OpenAI connection successful")
        return True
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False

def main():
    print("Testing API connections...\n")
    
    github_ok = test_github_connection()
    openai_ok = test_openai_connection()
    
    print(f"\nSummary:")
    print(f"GitHub API: {'✅ OK' if github_ok else '❌ FAILED'}")
    print(f"OpenAI API: {'✅ OK' if openai_ok else '❌ FAILED'}")
    
    if github_ok and openai_ok:
        print("\n🎉 All connections successful! You can run the main script.")
    else:
        print("\n⚠️  Some connections failed. Please check your API keys.")

if __name__ == "__main__":
    main()