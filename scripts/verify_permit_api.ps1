# Verify Permit Agent API (Sprint 7) - run after dev.ps1 / docker compose up
$ErrorActionPreference = "Stop"
$BaseUrl = if ($env:API_URL) { $env:API_URL } else { "http://localhost:8800" }

function Assert-Ok($condition, $label) {
    if (-not $condition) { throw "$label - check failed" }
    Write-Host "[OK] $label"
}

Write-Host "=== FleetPilot Permit API verification ==="
Write-Host "API: $BaseUrl"

docker ps 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker is not running. Start Docker Desktop (WSL2 required), then: .\dev.ps1"
}

Write-Host "`n--- Migration ---"
docker compose exec api alembic current
docker compose exec api alembic upgrade head

Write-Host "`n--- Seed demo (idempotent) ---"
docker compose exec api env PYTHONPATH=/app python scripts/seed_demo.py

Write-Host "`n--- Health ---"
$health = Invoke-RestMethod -Uri "$BaseUrl/api/v1/health" -Method Get
Assert-Ok ($health.status -eq "ok") "GET /api/v1/health"

Write-Host "`n--- Login ---"
$loginBody = @{ email = "demo@fleetpilot.ru"; password = "Demo12345!" } | ConvertTo-Json
$auth = Invoke-RestMethod -Uri "$BaseUrl/api/v1/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
$token = $auth.access_token
Assert-Ok ([bool]$token) "POST /api/v1/auth/login"
$headers = @{ Authorization = "Bearer $token" }

Write-Host "`n--- Rosdor health ---"
$rosdor = Invoke-RestMethod -Uri "$BaseUrl/api/v1/integrations/rosdor/health" -Method Get
Assert-Ok ($rosdor.provider -eq "rosdor_monitoring") "GET /integrations/rosdor/health"

Write-Host "`n--- Analyze route ---"
$analyzeBody = @{
    origin = @{ name = "Moscow" }
    destination = @{ name = "Saint Petersburg" }
    cargo = @{
        length_m = 15
        width_m = 3.2
        height_m = 4.1
        mass_kg = 48000
        axle_loads_kg = @(12000, 12000)
    }
    persist = $true
} | ConvertTo-Json -Depth 5
$analysis = Invoke-RestMethod -Uri "$BaseUrl/api/v1/agents/permit/analyze-route" -Method Post -Body $analyzeBody -ContentType "application/json" -Headers $headers
if (-not $analysis.analysis.permit_required) { throw "Expected permit_required=true" }
Assert-Ok ([bool]$analysis.permit_request_id) "POST /agents/permit/analyze-route"

$requestId = $analysis.permit_request_id

Write-Host "`n--- List requests ---"
$list = Invoke-RestMethod -Uri "$BaseUrl/api/v1/agents/permit/requests" -Method Get -Headers $headers
if ($list.total -lt 1) { throw "Expected at least 1 permit request" }
Assert-Ok $true "GET /agents/permit/requests"

Write-Host "`n--- Get request ---"
$detail = Invoke-RestMethod -Uri "$BaseUrl/api/v1/agents/permit/requests/$requestId" -Method Get -Headers $headers
Assert-Ok ($detail.id -eq $requestId) "GET /agents/permit/requests/{id}"

Write-Host "`n--- Approve (HITL) ---"
$approveBody = @{ notes = "Dispatcher verified"; external_permit_number = "DEMO-001" } | ConvertTo-Json
$approved = Invoke-RestMethod -Uri "$BaseUrl/api/v1/agents/permit/requests/$requestId/approve" -Method Post -Body $approveBody -ContentType "application/json" -Headers $headers
if ($approved.status -ne "approved") { throw "Expected status=approved" }
Assert-Ok $true "POST /agents/permit/requests/{id}/approve"

Write-Host "`n--- Registry check (DEMO stub) ---"
$checkBody = @{ permit_number = "DEMO-12345"; plate = "A123BC77" } | ConvertTo-Json
$check = Invoke-RestMethod -Uri "$BaseUrl/api/v1/integrations/rosdor/permits/check" -Method Post -Body $checkBody -ContentType "application/json" -Headers $headers
if (-not $check.found) { throw "Expected DEMO permit found=true" }
Assert-Ok $true "POST /integrations/rosdor/permits/check"

Write-Host "`n=== All Permit API checks passed ==="
