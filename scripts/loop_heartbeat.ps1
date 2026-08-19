param([int]$Seconds = 600)

$prompt = @'
FleetPilot smoke loop: run scripts/smoke_check.ps1 from repo root. Exit 2 means Docker is down - report only. Exit 1 means fix trivial regressions in apps/. Every 5th tick add -Ci for CI parity. Summarize changes.
'@.Trim()

Start-Sleep -Seconds $Seconds
$payload = @{ prompt = $prompt } | ConvertTo-Json -Compress
Write-Output "AGENT_LOOP_WAKE_fleetpilot_smoke $payload"
