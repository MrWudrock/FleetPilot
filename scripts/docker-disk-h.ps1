# Перенос Docker WSL disk image на H:\gradle_cache2
# Запускать после закрытия Docker Desktop (иконка в трее → Quit)

$ErrorActionPreference = "Stop"
$TargetRoot = "H:\gradle_cache2"
$OldWsl = Join-Path $env:LOCALAPPDATA "Docker\wsl"
$SettingsJson = Join-Path $env:APPDATA "Docker\settings.json"
$SettingsStore = Join-Path $env:APPDATA "Docker\settings-store.json"

Write-Host "=== Docker disk -> H:\gradle_cache2 ==="

New-Item -ItemType Directory -Path $TargetRoot -Force | Out-Null

@{
    customWslDistroDir = "H:\gradle_cache2"
} | ConvertTo-Json | Set-Content -Path $SettingsJson -Encoding UTF8

$store = Get-Content $SettingsStore -Raw | ConvertFrom-Json
$store | Add-Member -NotePropertyName CustomWslDistroDir -NotePropertyValue "H:\gradle_cache2" -Force
$store | ConvertTo-Json -Depth 10 | Set-Content -Path $SettingsStore -Encoding UTF8

Write-Host "Config updated:"
Write-Host "  $SettingsJson"
Write-Host "  $SettingsStore"
Write-Host "  customWslDistroDir = H:\gradle_cache2"
Write-Host ""
Write-Host "Docker создаст данные в: H:\gradle_cache2\DockerDesktopWSL"
Write-Host ""

if (Test-Path $OldWsl) {
    $vhdx = Get-ChildItem $OldWsl -Recurse -Filter "*.vhdx" -ErrorAction SilentlyContinue
    if ($vhdx) {
        Write-Host "Текущие диски на C: (можно перенести вручную после wsl --shutdown):"
        $vhdx | ForEach-Object { Write-Host "  $($_.FullName) — $([math]::Round($_.Length/1GB, 2)) GB" }
        Write-Host ""
        Write-Host "Опционально (сохранить образы):"
        Write-Host "  1. Quit Docker Desktop"
        Write-Host "  2. wsl --shutdown"
        Write-Host "  3. wsl --export docker-desktop-data `"$TargetRoot\docker-desktop-data.tar`""
        Write-Host "  4. wsl --unregister docker-desktop-data"
        Write-Host "  5. wsl --import docker-desktop-data `"$TargetRoot\data`" `"$TargetRoot\docker-desktop-data.tar`" --version 2"
        Write-Host "  6. Запустить Docker Desktop"
    }
}

Write-Host ""
Write-Host "Перезапустите Docker Desktop. Проверка: Settings -> Resources -> Advanced -> Disk image location"
