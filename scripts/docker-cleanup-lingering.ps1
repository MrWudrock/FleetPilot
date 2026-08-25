# Fix Docker Desktop "lingering processes detected" (stuck com.docker.build.exe).
# Run PowerShell as Administrator when Docker cannot kill the process itself.
#
# Typical cause: interrupted `docker compose build` / `docker compose up --build`
# (e.g. web npm install timeout or Ctrl+C in terminal).

$ErrorActionPreference = "Stop"

function Test-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $p = [Security.Principal.WindowsPrincipal]$id
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

Write-Host "=== Docker lingering process cleanup ===" -ForegroundColor Cyan

$dockerRootPids = @()
Get-CimInstance Win32_Process -Filter "Name='Docker Desktop.exe'" -ErrorAction SilentlyContinue |
    ForEach-Object { $dockerRootPids += $_.ProcessId }
Get-CimInstance Win32_Process -Filter "Name='com.docker.backend.exe'" -ErrorAction SilentlyContinue |
    ForEach-Object { $dockerRootPids += $_.ProcessId }

$buildProcs = Get-Process com.docker.build -ErrorAction SilentlyContinue
if (-not $buildProcs) {
    Write-Host "[OK] No com.docker.build.exe processes found." -ForegroundColor Green
    exit 0
}

$orphans = @()
foreach ($proc in $buildProcs) {
    $parent = (Get-CimInstance Win32_Process -Filter "ProcessId=$($proc.Id)" -ErrorAction SilentlyContinue).ParentProcessId
    $backendPid = (Get-CimInstance Win32_Process -Filter "ProcessId=$parent" -ErrorAction SilentlyContinue)
    $isUnderDocker = $backendPid -and $backendPid.Name -eq "com.docker.backend.exe"
    if (-not $isUnderDocker) {
        $orphans += [pscustomobject]@{ Id = $proc.Id; ParentId = $parent }
    }
}

if ($orphans.Count -eq 0) {
    Write-Host "[OK] com.docker.build.exe is attached to Docker backend (normal)." -ForegroundColor Green
    Write-Host "     If Docker Desktop still shows the warning, use: Troubleshoot -> Restart Docker Desktop"
    exit 0
}

Write-Host "Found $($orphans.Count) orphaned com.docker.build.exe process(es):" -ForegroundColor Yellow
$orphans | Format-Table -AutoSize

if (-not (Test-Admin)) {
    Write-Host ""
    Write-Host "Re-run this script as Administrator to kill orphaned build processes." -ForegroundColor Yellow
    Write-Host "  Right-click PowerShell -> Run as administrator"
    Write-Host "  cd `"$PSScriptRoot\..`""
    Write-Host "  .\scripts\docker-cleanup-lingering.ps1"
    exit 1
}

foreach ($item in $orphans) {
    Write-Host "Killing PID $($item.Id) (tree)..." -ForegroundColor Yellow
    taskkill /PID $item.Id /T /F | Out-Null
}

Start-Sleep -Seconds 2
$remaining = Get-Process com.docker.build -ErrorAction SilentlyContinue
if ($remaining) {
    Write-Host "[WARN] Some build processes remain. Restart Docker Desktop from the tray menu." -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Orphaned build processes removed." -ForegroundColor Green
Write-Host "Verify: docker version && docker ps"
