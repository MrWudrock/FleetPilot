# Локальный сервер для landing (без Node.js)
# Запуск: .\serve.ps1  или  powershell -File serve.ps1

$Port = 3000
$Root = $PSScriptRoot

Write-Host "FleetPilot landing -> http://localhost:$Port" -ForegroundColor Green
Write-Host "Wireframes     -> http://localhost:$Port/../wireframes/index.html" -ForegroundColor Green
Write-Host "Ctrl+C to stop" -ForegroundColor DarkGray

Set-Location $Root
& python -m http.server $Port
