# Локальный сервер для landing (без Node.js)
# Запуск: .\serve.ps1

param(
    [int]$Port = 3000
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

function Test-PortFree([int]$p) {
    $conn = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue
    return -not $conn
}

function Find-FreePort([int]$start) {
    for ($p = $start; $p -le ($start + 20); $p++) {
        if (Test-PortFree $p) { return $p }
    }
    throw "No free port found between $start and $($start + 20)"
}

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python not found. Install Python 3 and add it to PATH." -ForegroundColor Red
    Write-Host "Or use root server: cd .. ; .\serve.ps1" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-PortFree $Port)) {
    $busy = $Port
    $Port = Find-FreePort ($Port + 1)
    Write-Host "Port $busy is busy (often Docker/Next.js). Using port $Port instead." -ForegroundColor Yellow
}

$config = Join-Path $Root "config.js"
$example = Join-Path $Root "config.example.js"
if (-not (Test-Path $config) -and (Test-Path $example)) {
    Copy-Item $example $config
    Write-Host "Created config.js from config.example.js" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "FleetPilot landing  -> http://localhost:$Port/" -ForegroundColor Green
Write-Host "Wireframes          -> http://localhost:$Port/wireframes/" -ForegroundColor Green
Write-Host "Pitch deck          -> http://localhost:$Port/pitch-deck.html" -ForegroundColor Green
Write-Host "Ctrl+C to stop" -ForegroundColor DarkGray
Write-Host ""

Set-Location $Root
& python -m http.server $Port
