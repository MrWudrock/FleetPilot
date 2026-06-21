# Deploy FleetPilot landing to Vercel
# Usage: .\deploy.ps1
# Requires: Node.js (https://nodejs.org)

Set-Location $PSScriptRoot

function Find-Node {
    if (Get-Command node -ErrorAction SilentlyContinue) { return "node" }
    $p = "C:\Program Files\nodejs\node.exe"
    if (Test-Path $p) { return $p }
    return $null
}

$node = Find-Node
if (-not $node) {
    Write-Host "Node.js not found. Options:" -ForegroundColor Yellow
    Write-Host "  1. Install from https://nodejs.org and re-run .\deploy.ps1" -ForegroundColor White
    Write-Host "  2. Deploy via GitHub -> vercel.com/new (see VERCEL-DEPLOY.md)" -ForegroundColor White
    exit 1
}

Write-Host ">> Syncing wireframes + pitch-deck..." -ForegroundColor Cyan
& "$PSScriptRoot\sync-assets.ps1"

Write-Host ">> Building config.js..." -ForegroundColor Cyan
& $node generate-config.js
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ">> Checking Vercel auth..." -ForegroundColor Cyan
$who = & npx --yes vercel whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not logged in. Run:" -ForegroundColor Yellow
    Write-Host "  npx vercel login" -ForegroundColor White
    exit 1
}
Write-Host "Logged in: $who" -ForegroundColor Green

Write-Host ">> Deploying to production..." -ForegroundColor Cyan
& npx --yes vercel --prod
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ">> Done!" -ForegroundColor Green
Write-Host "Set env in Vercel Dashboard: FORMSPREE_ID, FORM_SUBMIT_EMAIL, YANDEX_METRIKA_ID" -ForegroundColor Cyan
