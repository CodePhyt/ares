# PowerShell script to create GitHub repository and push ARES

$REPO_NAME = "ares"
$GITHUB_USER = "CodePhyt"
$GITHUB_TOKEN = $env:GITHUB_TOKEN  # Use environment variable

Write-Host "🛡️ ARES - GitHub Repository Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if repository exists
Write-Host "Checking if repository exists..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "token $GITHUB_TOKEN"
    "Accept" = "application/vnd.github.v3+json"
}

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/$GITHUB_USER/$REPO_NAME" -Headers $headers -Method Get
    Write-Host "✅ Repository already exists" -ForegroundColor Green
} catch {
    Write-Host "📦 Creating new repository: $REPO_NAME" -ForegroundColor Yellow
    
    $body = @{
        name = $REPO_NAME
        description = "ARES - Autonomous Resilient Enterprise Suite: GDPR-compliant, 100% offline AI Command Center for German enterprises"
        private = $false
        has_issues = $true
        has_projects = $true
        has_wiki = $false
        auto_init = $false
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Headers $headers -Method Post -Body $body -ContentType "application/json"
        Write-Host "✅ Repository created successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error creating repository: $_" -ForegroundColor Red
        exit 1
    }
}

# Configure remote
Write-Host ""
Write-Host "Configuring Git remote..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin "https://$GITHUB_TOKEN@github.com/$GITHUB_USER/$REPO_NAME.git"

# Ensure we're on main branch
git branch -M main

# Push to GitHub
Write-Host ""
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Cyan
git push -u origin main

Write-Host ""
Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
Write-Host ""
Write-Host "Repository URL: https://github.com/$GITHUB_USER/$REPO_NAME" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Visit https://github.com/$GITHUB_USER/$REPO_NAME"
Write-Host "2. Add repository topics: ai, rag, gdpr, enterprise, german, fastapi, streamlit"
Write-Host "3. Create initial release (v1.0.0)"
Write-Host "4. Set up branch protection rules"
