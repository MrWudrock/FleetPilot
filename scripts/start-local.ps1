# Start FleetPilot local backend (Docker API) - required for Desktop login
# Usage (from repo root):
#   .\scripts\start-local.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

function Test-DockerEngine {
    try {
        docker info 2>$null | Out-Null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

Write-Host "=== FleetPilot local start ===" -ForegroundColor Cyan

if (-not (Test-DockerEngine)) {
    Write-Host "Docker engine ne otvechaet. Zapuskayu Docker Desktop..." -ForegroundColor Yellow
    $dockerExe = Join-Path $env:ProgramFiles "Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerExe) {
        Start-Process $dockerExe
    } else {
        throw "Docker Desktop not found. Install Docker Desktop (WSL2)."
    }

    $ok = $false
    for ($i = 1; $i -le 60; $i++) {
        Start-Sleep -Seconds 3
        if (Test-DockerEngine) { $ok = $true; break }
        Write-Host ("  [{0}/60] waiting for engine..." -f $i)
    }
    if (-not $ok) {
        Write-Host "Docker engine failed to start." -ForegroundColor Red
        Write-Host "Fix WSL (Admin PowerShell): .\scripts\enable-wsl.ps1" -ForegroundColor Yellow
        Write-Host "Then reboot if needed, start Docker Desktop, re-run this script." -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "Starting postgres + redis + api..." -ForegroundColor Cyan
docker compose up -d postgres redis api
if ($LASTEXITCODE -ne 0) { throw "docker compose up failed" }

$healthy = $false
for ($i = 1; $i -le 40; $i++) {
    Start-Sleep -Seconds 2
    try {
        $h = Invoke-RestMethod -Uri "http://localhost:8800/api/v1/health" -TimeoutSec 3
        if ($h.status -eq "ok") { $healthy = $true; break }
    } catch {
        Write-Host ("  [{0}/40] API not ready..." -f $i)
    }
}

if (-not $healthy) {
    Write-Host "API did not answer on :8800. Logs:" -ForegroundColor Red
    docker compose logs api --tail 40
    exit 1
}

Write-Host "API OK: http://localhost:8800" -ForegroundColor Green

try {
    $login = Invoke-RestMethod -Method Post -Uri "http://localhost:8800/api/v1/auth/login" `
        -ContentType "application/json" `
        -Body '{"email":"demo@fleetpilot.ru","password":"Demo12345!"}' `
        -TimeoutSec 10
    if ($login.access_token) {
        Write-Host "Demo login OK (demo@fleetpilot.ru)" -ForegroundColor Green
    }
} catch {
    Write-Host "Demo user missing - running seed..." -ForegroundColor Yellow
    docker compose exec -T api env PYTHONPATH=/app python scripts/seed_demo.py
}

Write-Host ""
Write-Host "Ready. Next steps:" -ForegroundColor Cyan
Write-Host "  1) Start FleetPilot Desktop"
Write-Host "  2) API URL on login screen: http://localhost:8800"
Write-Host "  3) Login: demo@fleetpilot.ru / Demo12345!"
Write-Host ""
Write-Host "Checks:"
Write-Host "  Invoke-RestMethod http://localhost:8800/api/v1/health"
Write-Host "  docker compose ps"