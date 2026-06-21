# Корневой сервер — landing + wireframes + docs
# Запуск из корня проекта: .\serve.ps1

$Port = 8080
$Root = $PSScriptRoot

Write-Host "FleetPilot project server -> http://localhost:$Port" -ForegroundColor Green
Write-Host "  Landing:    http://localhost:$Port/landing/" -ForegroundColor Cyan
Write-Host "  Wireframes: http://localhost:$Port/wireframes/" -ForegroundColor Cyan
Write-Host "Ctrl+C to stop" -ForegroundColor DarkGray

Set-Location $Root
& python -m http.server $Port
