#!/bin/bash
# Script to create GitHub repository and push ARES

set -e

REPO_NAME="ares"
GITHUB_USER="CodePhyt"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"  # Use environment variable or set here

echo "🛡️ ARES - GitHub Repository Setup"
echo "=================================="
echo ""

# Check if repository exists
echo "Checking if repository exists..."
if curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$GITHUB_USER/$REPO_NAME" | grep -q '"name"'; then
    echo "✅ Repository already exists"
else
    echo "📦 Creating new repository: $REPO_NAME"
    
    # Create repository
    curl -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/user/repos" \
        -d "{
            \"name\": \"$REPO_NAME\",
            \"description\": \"ARES - Autonomous Resilient Enterprise Suite: GDPR-compliant, 100% offline AI Command Center for German enterprises\",
            \"private\": false,
            \"has_issues\": true,
            \"has_projects\": true,
            \"has_wiki\": false,
            \"auto_init\": false
        }"
    
    echo ""
    echo "✅ Repository created successfully"
fi

# Configure remote
echo ""
echo "Configuring Git remote..."
git remote remove origin 2>/dev/null || true
git remote add origin "https://$GITHUB_TOKEN@github.com/$GITHUB_USER/$REPO_NAME.git"

# Ensure we're on main branch
git branch -M main

# Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Successfully pushed to GitHub!"
echo ""
echo "Repository URL: https://github.com/$GITHUB_USER/$REPO_NAME"
echo ""
echo "Next steps:"
echo "1. Visit https://github.com/$GITHUB_USER/$REPO_NAME"
echo "2. Add repository topics: ai, rag, gdpr, enterprise, german, fastapi, streamlit"
echo "3. Create initial release (v1.0.0)"
echo "4. Set up branch protection rules"
