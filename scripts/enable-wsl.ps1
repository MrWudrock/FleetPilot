# Включение WSL (исправление Wsl/0x80070422)
# Запуск: PowerShell от имени администратора
#   Set-ExecutionPolicy Bypass -Scope Process -Force
#   cd "C:\Users\Wu\develop\startapp log"
#   .\scripts\enable-wsl.ps1

$ErrorActionPreference = "Stop"

function Require-Admin {
    $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Error "Запустите PowerShell от имени администратора."
    }
}

Require-Admin

Write-Host "=== Включение компонентов Windows ==="
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

Write-Host "`n=== Включение службы WslService ==="
sc.exe config WslService start= demand
sc.exe config LxssManager start= demand
Start-Service WslService -ErrorAction SilentlyContinue
Start-Service LxssManager -ErrorAction SilentlyContinue

Write-Host "`n=== Обновление WSL (если установлен) ==="
if (Test-Path "$env:ProgramFiles\WSL\wsl.exe") {
    & "$env:ProgramFiles\WSL\wsl.exe" --update
    & "$env:ProgramFiles\WSL\wsl.exe" --set-default-version 2
}

Write-Host "`n=== Статус ==="
Get-Service WslService, LxssManager -ErrorAction SilentlyContinue | Format-Table Name, Status, StartType -AutoSize

Write-Host @"

Готово. Если DISM запросил перезагрузку — перезагрузите ПК.

После перезагрузки:
  wsl --status
  wsl --shutdown
  Запустите Docker Desktop

"@
