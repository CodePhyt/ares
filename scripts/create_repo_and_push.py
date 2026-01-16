#!/usr/bin/env python3
"""
Create GitHub repository and push ARES code.
"""

import requests
import subprocess
import sys
import os
from pathlib import Path

GITHUB_USER = "CodePhyt"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")  # Use environment variable
REPO_NAME = "ares"

def create_repository():
    """Create GitHub repository using API."""
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    data = {
        "name": REPO_NAME,
        "description": "ARES - Autonomous Resilient Enterprise Suite: GDPR-compliant, 100% offline AI Command Center for German enterprises",
        "private": False,
        "has_issues": True,
        "has_projects": True,
        "has_wiki": False,
        "auto_init": False,
    }
    
    # Check if repository exists
    check_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}"
    response = requests.get(check_url, headers=headers)
    
    if response.status_code == 200:
        print("✅ Repository already exists")
        return True
    
    # Create repository
    print(f"📦 Creating repository: {REPO_NAME}")
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 201:
        print("✅ Repository created successfully")
        return True
    elif response.status_code == 422:
        print("⚠️  Repository might already exist or name is invalid")
        return True  # Continue anyway
    else:
        print(f"❌ Error creating repository: {response.status_code}")
        print(response.text)
        return False

def push_to_github():
    """Push code to GitHub."""
    repo_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{REPO_NAME}.git"
    
    # Remove existing remote
    subprocess.run(["git", "remote", "remove", "origin"], 
                   capture_output=True, cwd=Path.cwd())
    
    # Add new remote
    subprocess.run(["git", "remote", "add", "origin", repo_url],
                   cwd=Path.cwd(), check=True)
    
    # Ensure main branch
    subprocess.run(["git", "branch", "-M", "main"],
                   cwd=Path.cwd(), check=True)
    
    # Push to GitHub
    print("📤 Pushing to GitHub...")
    result = subprocess.run(["git", "push", "-u", "origin", "main"],
                           cwd=Path.cwd())
    
    if result.returncode == 0:
        print("✅ Successfully pushed to GitHub!")
        print(f"\nRepository URL: https://github.com/{GITHUB_USER}/{REPO_NAME}")
        return True
    else:
        print("❌ Error pushing to GitHub")
        return False

def main():
    """Main function."""
    print("🛡️ ARES - GitHub Repository Setup")
    print("=" * 40)
    print()
    
    # Create repository
    if not create_repository():
        sys.exit(1)
    
    print()
    
    # Push code
    if not push_to_github():
        sys.exit(1)
    
    print()
    print("Next steps:")
    print(f"1. Visit https://github.com/{GITHUB_USER}/{REPO_NAME}")
    print("2. Add repository topics: ai, rag, gdpr, enterprise, german, fastapi, streamlit")
    print("3. Create initial release (v1.0.0)")
    print("4. Set up branch protection rules")

if __name__ == "__main__":
    main()
