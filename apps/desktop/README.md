# FleetPilot Desktop (Windows)

Облачный клиент: Electron-окно с UI FleetPilot, данные через API.

## Требования

- Node.js 20+
- Windows x64
- Для пилота: API на `http://localhost:8800` (`docker compose up -d postgres redis api`)

## Ежедневный запуск (чтобы не было Failed to fetch)

```powershell
cd "C:\Users\Wu\develop\startapp log"
.\scripts\start-local.ps1   # Docker + API на :8800
# затем ярлык FleetPilot Desktop
```

Логин: `demo@fleetpilot.ru` / `Demo12345!`  
Полная инструкция: [`docs/RUNBOOK.md`](../../docs/RUNBOOK.md)

## Dev


```powershell
cd apps/web
npm install
$env:NEXT_PUBLIC_API_URL="http://localhost:8800"
npm run build

cd ../desktop
npm install
npm run build:web
npm run dev
```

## Сборка установщика

```powershell
cd apps/desktop
npm install
npm run dist:win
```

Артефакт: `apps/desktop/release/FleetPilot-Setup-0.1.0.exe`

Публикация на лендинг:

```powershell
.\scripts\publish-desktop.ps1
```

из корня репозитория, либо:

```powershell
cd apps/desktop
npm run dist:win
Copy-Item .\release\FleetPilot-Setup-*.exe ..\..\landing\downloads\FleetPilot-Setup.exe -Force
```

## Конфиг API

Файл: `%APPDATA%\FleetPilot\config.json`

```json
{ "apiUrl": "http://localhost:8800" }
```

В UI: **Настройки → URL API**. После смены URL перезапустите приложение или обновите страницу.
