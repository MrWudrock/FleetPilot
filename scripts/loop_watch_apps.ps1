# Watches FleetPilot apps/ for changes; emits loop wake sentinel once per burst.
param(
    [string]$Root = (Split-Path $PSScriptRoot -Parent),
    [int]$PollSeconds = 45,
    [int]$QuietSeconds = 120
)

$watchDirs = @(
    (Join-Path $Root "apps\api\app"),
    (Join-Path $Root "apps\web\src"),
    (Join-Path $Root "apps\api\alembic")
)

$prompt = 'FleetPilot smoke loop: run scripts/smoke_check.ps1 from repo root. If exit 2 (Docker down), report only. If exit 1, diagnose and fix trivial regressions in apps/. If -Ci requested in prior context, use smoke_check.ps1 -Ci. Summarize changes since last tick.'

function Get-LatestWrite($dirs) {
    $latest = [datetime]::MinValue
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) { continue }
        Get-ChildItem -Path $dir -Recurse -File -ErrorAction SilentlyContinue |
            ForEach-Object { if ($_.LastWriteTime -gt $latest) { $latest = $_.LastWriteTime } }
    }
    return $latest
}

$baseline = Get-LatestWrite $watchDirs
Write-Host "AGENT_LOOP_WATCHER fleetpilot_smoke armed (baseline=$baseline)"

while ($true) {
    Start-Sleep -Seconds $PollSeconds
    $current = Get-LatestWrite $watchDirs
    if ($current -gt $baseline) {
        $baseline = $current
        $json = ($prompt -replace '"', '\"')
        Write-Output "AGENT_LOOP_WAKE_fleetpilot_smoke {`"prompt`":`"$json`"}"
        Start-Sleep -Seconds $QuietSeconds
        $baseline = Get-LatestWrite $watchDirs
    }
}
