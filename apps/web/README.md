# FleetPilot Web

Next.js 15 + React 19 cabinet (static export for Electron Desktop).

## Dev

```powershell
cd apps\web
$env:NEXT_PUBLIC_API_URL = "http://localhost:8800"
npm run dev
```

API must be up: from repo root `.\scripts\start-local.ps1`.

## Tests

```powershell
cd apps\web

# Unit (offline)
npm test

# E2E login smoke — needs API :8800 and web :3000
npm run test:e2e:install   # once
npm run dev                # other terminal
npm run test:e2e

# Skip when API is down
$env:PLAYWRIGHT_SKIP_API = "1"
npm run test:e2e
```

## Build (static export for Desktop)

```powershell
$env:NEXT_PUBLIC_API_URL = "http://localhost:8800"
npm run build
# output -> out/
```

## Architecture notes

- Server state: TanStack Query (`providers.tsx`, `lib/query-keys.ts`)
- Shell: `AppShell` + grouped `Sidebar`
- Auth: JWT in localStorage + `AuthGuard`
