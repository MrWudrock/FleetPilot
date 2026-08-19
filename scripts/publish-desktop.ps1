# Publish FleetPilot Windows installer to landing/downloads

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$desktop = Join-Path $root "apps\desktop"
$release = Join-Path $desktop "release"
$destDir = Join-Path $root "landing\downloads"
$dest = Join-Path $destDir "FleetPilot-Setup.exe"

Set-Location $desktop
if (-not (Test-Path "node_modules\electron")) {
  npm install
}

Write-Host "Building web UI + Windows installer..."
npm run dist:win

$built = Get-ChildItem -Path $release -Filter "FleetPilot-Setup-*.exe" |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

if (-not $built) {
  throw "Installer not found in $release"
}

New-Item -ItemType Directory -Force -Path $destDir | Out-Null
Copy-Item $built.FullName $dest -Force
Write-Host "Published: $($built.Name) -> $dest"
Write-Host "Size: $([math]::Round($built.Length / 1MB, 1)) MB"
