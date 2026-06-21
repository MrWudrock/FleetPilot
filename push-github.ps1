# Push FleetPilot to GitHub
# Usage: .\push-github.ps1 -GitHubUser "your-username" [-RepoName "fleetpilot"]

param(
    [Parameter(Mandatory = $true)]
    [string]$GitHubUser,

    [string]$RepoName = "fleetpilot"
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location $Root

$remoteUrl = "https://github.com/$GitHubUser/$RepoName.git"

Write-Host "FleetPilot -> GitHub" -ForegroundColor Cyan
Write-Host "  Remote: $remoteUrl" -ForegroundColor Gray

$existing = git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Remote 'origin' already exists: $existing" -ForegroundColor Yellow
    $ans = Read-Host "Replace with $remoteUrl? (y/N)"
    if ($ans -eq "y" -or $ans -eq "Y") {
        git remote set-url origin $remoteUrl
    }
} else {
    git remote add origin $remoteUrl
}

Write-Host ""
Write-Host "Before push, create an EMPTY repo on GitHub:" -ForegroundColor Yellow
Write-Host "  https://github.com/new?name=$RepoName" -ForegroundColor White
Write-Host "  (no README, no .gitignore)" -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter when repo is created on GitHub"

Write-Host "Pushing branch main..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Done! Next: Vercel autodeploy" -ForegroundColor Green
    Write-Host "  https://vercel.com/new" -ForegroundColor White
    Write-Host "  Root Directory: landing" -ForegroundColor White
    Write-Host "  Build Command: node generate-config.js" -ForegroundColor White
    Write-Host "  Guide: docs/GITHUB-VERCEL-SETUP.md" -ForegroundColor Gray
} else {
    Write-Host "Push failed. See docs/GITHUB-VERCEL-SETUP.md" -ForegroundColor Red
    exit 1
}
