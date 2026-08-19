# FleetPilot Scan — build graph + serve interactive map
# Usage: .\scan\serve.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "=== FleetPilot Scan ===" -ForegroundColor Cyan

$python = $null
foreach ($c in @("python", "py", "python3")) {
    if (Get-Command $c -ErrorAction SilentlyContinue) {
        $python = $c
        break
    }
}
if (-not $python) { throw "Python not found. Install Python 3.11+." }

Write-Host "Building graph..." -ForegroundColor Cyan
& $python scan/build_graph.py
if ($LASTEXITCODE -ne 0) { throw "build_graph.py failed" }

$port = 8787
Write-Host "Serving scan at http://localhost:$port" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop." -ForegroundColor DarkGray

Set-Location scan
if (Get-Command python -ErrorAction SilentlyContinue) {
    python -m http.server $port
} else {
    py -m http.server $port
}
