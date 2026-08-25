# Корневой сервер — landing + wireframes + docs
# Запуск из корня проекта: .\serve.ps1

param(
    [int]$Port = 8080
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
    exit 1
}

if (-not (Test-PortFree $Port)) {
    $busy = $Port
    $Port = Find-FreePort ($Port + 1)
    Write-Host "Port $busy is busy. Using port $Port instead." -ForegroundColor Yellow
}

$landingConfig = Join-Path $Root "landing\config.js"
$landingExample = Join-Path $Root "landing\config.example.js"
if (-not (Test-Path $landingConfig) -and (Test-Path $landingExample)) {
    Copy-Item $landingExample $landingConfig
    Write-Host "Created landing/config.js from config.example.js" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "FleetPilot project server -> http://localhost:$Port" -ForegroundColor Green
Write-Host "  Landing:    http://localhost:$Port/landing/" -ForegroundColor Cyan
Write-Host "  Wireframes: http://localhost:$Port/wireframes/" -ForegroundColor Cyan
Write-Host "Ctrl+C to stop" -ForegroundColor DarkGray
Write-Host ""

Set-Location $Root
& python -m http.server $Port
