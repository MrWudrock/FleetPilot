# Sync wireframes + pitch-deck into landing/ before Vercel deploy

$Root = Split-Path $PSScriptRoot -Parent

Write-Host "Syncing assets to landing/..." -ForegroundColor Cyan

$wireSrc = Join-Path $Root "wireframes\index.html"
$wireDst = Join-Path $PSScriptRoot "wireframes\index.html"
New-Item -ItemType Directory -Force -Path (Split-Path $wireDst) | Out-Null
Copy-Item $wireSrc $wireDst -Force
Write-Host "  wireframes/index.html" -ForegroundColor Green

$deckSrc = Join-Path $Root "docs\fleet-ai\pitch-deck.html"
$deckDst = Join-Path $PSScriptRoot "pitch-deck.html"
Copy-Item $deckSrc $deckDst -Force
Write-Host "  pitch-deck.html" -ForegroundColor Green

Write-Host "Done." -ForegroundColor Green
