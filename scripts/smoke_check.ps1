# FleetPilot stack smoke check - fast health + readiness (Sprint 1 exit criteria)
# Usage: .\scripts\smoke_check.ps1 [-Ci]
# Exit: 0 = all checks passed, 1 = failure, 2 = docker/stack not running (skip)
param(
    [switch]$Ci
)

$ErrorActionPreference = "Continue"
$Root = Split-Path $PSScriptRoot -Parent
$BaseUrl = if ($env:API_URL) { $env:API_URL } else { "http://localhost:8800" }

$results = [ordered]@{}
$failures = @()

function Record {
    param($Name, $Ok, $Detail)
    $results[$Name] = @{ ok = $Ok; detail = $Detail }
    if (-not $Ok) { $script:failures += $Name }
    $mark = if ($Ok) { "[OK]" } else { "[FAIL]" }
    Write-Host "$mark $Name - $Detail"
}

Write-Host "=== FleetPilot smoke check ==="
Write-Host "Root: $Root"
Write-Host "API:  $BaseUrl"
Write-Host ""

try {
    docker info 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "docker info failed" }
    Record -Name "docker_daemon" -Ok $true -Detail "running"
}
catch {
    Record -Name "docker_daemon" -Ok $false -Detail $_.Exception.Message
    Write-Host ""
    Write-Host "SKIP: start Docker Desktop, then: .\dev.ps1"
    exit 2
}

Push-Location $Root
try {
    $psOut = docker compose ps --format json 2>&1
    if ($LASTEXITCODE -ne 0) { throw ($psOut -join "`n") }

    $services = @()
    foreach ($line in ($psOut -split "`n")) {
        $trimmed = $line.Trim()
        if ($trimmed) { $services += ($trimmed | ConvertFrom-Json) }
    }

    foreach ($name in @("postgres", "redis", "api")) {
        $svc = $services | Where-Object { $_.Service -eq $name -or $_.Name -match $name } | Select-Object -First 1
        if (-not $svc) {
            Record -Name "compose_$name" -Ok $false -Detail "service not found - run .\dev.ps1"
            continue
        }
        $detail = $svc.State
        if ($svc.Health) { $detail = "$detail ($($svc.Health))" }
        $ok = ($svc.State -eq "running") -and (($null -eq $svc.Health) -or ($svc.Health -eq "healthy"))
        Record -Name "compose_$name" -Ok $ok -Detail $detail
    }
}
catch {
    Record -Name "compose_status" -Ok $false -Detail $_.Exception.Message
}
finally {
    Pop-Location
}

function Invoke-Api {
    param([string]$Path)
    try {
        return Invoke-RestMethod -Uri "$BaseUrl$Path" -Method Get -TimeoutSec 5
    }
    catch {
        return $null
    }
}

$health = Invoke-Api -Path "/api/v1/health"
$healthDetail = if ($health) { $health.status } else { "unreachable" }
Record -Name "api_health" -Ok ($health.status -eq "ok") -Detail $healthDetail

$ready = Invoke-Api -Path "/api/v1/health/ready"
$readyOk = $false
$readyDetail = "unreachable"
if ($ready) {
    $readyOk = ($ready.status -eq "ok")
    $pg = $ready.checks.postgres.status
    $rd = $ready.checks.redis.status
    $readyDetail = "$($ready.status) (postgres=$pg, redis=$rd)"
}
Record -Name "api_ready" -Ok $readyOk -Detail $readyDetail

$meta = Invoke-Api -Path "/api/v1/meta/db"
$metaOk = $false
$metaDetail = "unreachable"
if ($meta) {
    $metaOk = ($meta.migration -and $meta.migration -ne "not_applied")
    $metaDetail = "migration=$($meta.migration)"
}
Record -Name "db_meta" -Ok $metaOk -Detail $metaDetail

if ($Ci) {
    Write-Host ""
    Write-Host "--- CI parity (app-ci.yml) ---"
    Push-Location (Join-Path $Root "apps\api")
    python -m compileall app alembic scripts 2>&1 | Out-Null
    Record -Name "api_compileall" -Ok ($LASTEXITCODE -eq 0) -Detail "python -m compileall"
    Pop-Location

    Push-Location (Join-Path $Root "apps\web")
    $prev = $env:NEXT_PUBLIC_API_URL
    $env:NEXT_PUBLIC_API_URL = "http://localhost:8000"
    npm run build 2>&1 | Out-Null
    Record -Name "web_build" -Ok ($LASTEXITCODE -eq 0) -Detail "npm run build"
    if ($null -ne $prev) { $env:NEXT_PUBLIC_API_URL = $prev }
    else { Remove-Item Env:NEXT_PUBLIC_API_URL -ErrorAction SilentlyContinue }
    Pop-Location
}

Write-Host ""
if ($failures.Count -eq 0) {
    Write-Host "=== All smoke checks passed ($($results.Count)) ==="
    exit 0
}

Write-Host "=== FAILED: $($failures -join ', ') ==="
exit 1
