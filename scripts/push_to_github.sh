#!/bin/bash
# Helper script to push ARES to GitHub

set -e

echo "🛡️ ARES - GitHub Push Helper"
echo "=============================="
echo ""

# Check if remote exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "✅ Remote 'origin' already configured"
    git remote -v
else
    echo "⚠️  No remote configured"
    echo ""
    read -p "Enter GitHub repository URL (e.g., https://github.com/username/repo.git): " repo_url
    
    if [ -z "$repo_url" ]; then
        echo "❌ No URL provided. Exiting."
        exit 1
    fi
    
    git remote add origin "$repo_url"
    echo "✅ Remote added: $repo_url"
fi

echo ""
echo "Current branch: $(git branch --show-current)"
echo ""

# Check if we're on main/master
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ] && [ "$current_branch" != "master" ]; then
    echo "⚠️  Not on main/master branch. Switching to main..."
    git checkout -b main 2>/dev/null || git checkout main
fi

# Rename to main if on master
if [ "$current_branch" = "master" ]; then
    git branch -M main
fi

echo ""
echo "📤 Pushing to GitHub..."
echo ""

# Push with token support
if [ -n "$GITHUB_TOKEN" ]; then
    echo "Using GITHUB_TOKEN environment variable"
    git push -u origin main
else
    echo "When prompted for password, use your GitHub Personal Access Token"
    echo "Token: ghp_..."
    git push -u origin main
fi

echo ""
echo "✅ Push completed!"
echo ""
echo "Next steps:"
echo "1. Verify repository on GitHub"
echo "2. Set up branch protection rules"
echo "3. Configure GitHub Actions secrets (if needed)"
echo "4. Create initial release (v1.0.0)"
