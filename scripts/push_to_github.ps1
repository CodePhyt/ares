# PowerShell script to push ARES to GitHub

Write-Host "🛡️ ARES - GitHub Push Helper" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Check if remote exists
try {
    $remoteUrl = git remote get-url origin 2>$null
    if ($remoteUrl) {
        Write-Host "✅ Remote 'origin' already configured" -ForegroundColor Green
        git remote -v
    }
} catch {
    Write-Host "⚠️  No remote configured" -ForegroundColor Yellow
    Write-Host ""
    $repoUrl = Read-Host "Enter GitHub repository URL (e.g., https://github.com/username/repo.git)"
    
    if ([string]::IsNullOrWhiteSpace($repoUrl)) {
        Write-Host "❌ No URL provided. Exiting." -ForegroundColor Red
        exit 1
    }
    
    git remote add origin $repoUrl
    Write-Host "✅ Remote added: $repoUrl" -ForegroundColor Green
}

Write-Host ""
$currentBranch = git branch --show-current
Write-Host "Current branch: $currentBranch"
Write-Host ""

# Check if we're on main/master
if ($currentBranch -ne "main" -and $currentBranch -ne "master") {
    Write-Host "⚠️  Not on main/master branch. Switching to main..." -ForegroundColor Yellow
    git checkout -b main 2>$null
    if ($LASTEXITCODE -ne 0) {
        git checkout main
    }
}

# Rename to main if on master
if ($currentBranch -eq "master") {
    git branch -M main
}

Write-Host ""
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Cyan
Write-Host ""

# Check for token in environment
if ($env:GITHUB_TOKEN) {
    Write-Host "Using GITHUB_TOKEN environment variable" -ForegroundColor Green
    git push -u origin main
} else {
    Write-Host "When prompted for password, use your GitHub Personal Access Token" -ForegroundColor Yellow
    Write-Host "Token: ghp_..." -ForegroundColor Yellow
    git push -u origin main
}

Write-Host ""
Write-Host "✅ Push completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Verify repository on GitHub"
Write-Host "2. Set up branch protection rules"
Write-Host "3. Configure GitHub Actions secrets (if needed)"
Write-Host "4. Create initial release (v1.0.0)"
