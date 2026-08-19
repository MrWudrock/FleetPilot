# FleetPilot — инструкция запуска приложения

**ОС:** Windows 10/11 (PowerShell)  
**Рекомендуемый способ:** Docker Compose + Desktop / Web  
**Дата:** 18.07.2026

---

## 0. Самая частая ошибка: `Failed to fetch` при входе

Это **не неверный пароль**. Приложение не смогло достучаться до API на `http://localhost:8800`.

**Что сделать:**

1. Запустить **Docker Desktop** → дождаться **Engine running**
2. В корне проекта:
   ```powershell
   cd "C:\Users\Wu\develop\startapp log"
   .\scripts\start-local.ps1
   ```
3. Проверить: http://localhost:8800/api/v1/health → `{"status":"ok",...}`
4. Открыть **FleetPilot Desktop**, URL API = `http://localhost:8800`
5. Логин: `demo@fleetpilot.ru` / `Demo12345!`

Если Docker пишет `unable to start` / WSL `0x80070422` — от администратора:

```powershell
.\scripts\enable-wsl.ps1
```

затем перезагрузка ПК при необходимости и снова Docker Desktop.

---

## 1. Что запускается

| Сервис | Порт | URL |
|--------|------|-----|
| **Desktop** (Electron) | — | установщик / ярлык FleetPilot |
| **Web** (кабинет Next.js) | 3000 | http://localhost:3000 |
| **API** (FastAPI) | **8800** | http://localhost:8800 |
| OpenAPI / Swagger | 8800 | http://localhost:8800/docs |
| Health | 8800 | http://localhost:8800/api/v1/health |
| PostgreSQL | 5432 | `localhost:5432` |
| Redis | 6379 | `localhost:6379` |

> Desktop — это только UI. **Без Docker API на :8800 вход не работает.**

> **UI:** не поднимайте Docker-сервис `web` (профиль `docker-web`) параллельно с локальным Next — на :3000 будет конфликт и старый `node_modules` без зависимостей. Для кабинета: `cd apps\web; npm run dev`.

---

## 2. Пошаговый запуск (ежедневно)

### Шаг A — Backend (обязательно)

```powershell
cd "C:\Users\Wu\develop\startapp log"
.\scripts\start-local.ps1
```

Скрипт: поднимет Docker при необходимости → `postgres` + `redis` + `api` → проверит health → проверит демо-логин.

### Шаг B — Клиент (выберите один)

**Вариант 1 — Desktop (скачанный .exe)**

1. Установите / запустите `FleetPilot` (или `landing\downloads\FleetPilot-Setup.exe`)
2. На экране входа: URL API = `http://localhost:8800`
3. Статус должен стать **API онлайн**
4. Email / пароль ниже

**Вариант 2 — Web в браузере**

```powershell
cd "C:\Users\Wu\develop\startapp log\apps\web"
$env:NEXT_PUBLIC_API_URL = "http://localhost:8800"
npm run dev
```

Открыть: http://localhost:3000/login

### Шаг C — Демо-доступ

| Поле | Значение |
|------|----------|
| Email | `demo@fleetpilot.ru` |
| Password | `Demo12345!` |

Если логин «Invalid email or password»:

```powershell
.\seed-demo.ps1
```

---

## 3. Чеклист проверки

- [ ] `docker version` показывает **Server**
- [ ] `docker compose ps` — postgres/redis **healthy**, api **Up**
- [ ] http://localhost:8800/api/v1/health → `ok`
- [ ] Desktop / login показывает **API онлайн**
- [ ] Вход `demo@fleetpilot.ru` / `Demo12345!` → Dashboard
- [ ] Меню: Карта, Топливо, Маршруты, ТО, Настройки открываются

Быстрая проверка API из PowerShell:

```powershell
Invoke-RestMethod http://localhost:8800/api/v1/health
Invoke-RestMethod -Method Post http://localhost:8800/api/v1/auth/login `
  -ContentType "application/json" `
  -Body '{"email":"demo@fleetpilot.ru","password":"Demo12345!"}'
```

Должен вернуться `access_token`.

---

## 4. Desktop: сборка и скачивание с сайта

```powershell
cd "C:\Users\Wu\develop\startapp log"
.\scripts\publish-desktop.ps1
```

Файл для лендинга: `landing\downloads\FleetPilot-Setup.exe`  
Кнопка на сайте: **Скачать для Windows** → `/downloads/FleetPilot-Setup.exe`

Подробнее: [`apps/desktop/README.md`](../apps/desktop/README.md)

---

## 5. Требования

| Компонент | Минимум |
|-----------|---------|
| Docker Desktop | 4.x, engine **Linux / WSL2** |
| WSL2 | Включён (`wsl --status`), служба **WslService** не Disabled |
| RAM | ≥ 8 GB свободно для Docker |
| Node.js 20+ | только для web/desktop сборки |
| PowerShell | 5.1+ |

---

## 6. Полезные команды

```powershell
docker compose ps
docker compose logs -f api
docker compose restart api
docker compose down          # остановить (данные БД сохранятся)
docker compose down -v       # полный сброс БД
.\seed-demo.ps1
.\scripts\verify_permit_api.ps1
```

---

## 7. Типичные проблемы

| Симптом | Решение |
|---------|---------|
| `Failed to fetch` | API не запущен → `.\scripts\start-local.ps1` |
| Docker unable to start / `0x80070422` | `.\scripts\enable-wsl.ps1` (админ) + reboot |
| Invalid email or password | `.\seed-demo.ps1` |
| Порт 8000 занят | API снаружи на **8800** — так и задумано |
| Desktop всё ещё на api.fleetpilot.ru | На форме входа укажите `http://localhost:8800` → OK |
| `SECRET_KEY is the insecure default` при старте API | В проде задайте уникальный `SECRET_KEY` и `DEBUG=false`. Локально оставьте `DEBUG=true` в compose |
| `/docs` 404 | Документация OpenAPI только при `DEBUG=true` |
| 403 на PATCH `/settings` | Менять настройки может только роль `admin` |
| 403 на POST `/auth/signup` | В prod `ALLOW_PUBLIC_SIGNUP=false` — используйте invite flow |
| `CREDENTIALS_ENCRYPTION_KEY` required | В prod задайте отдельный ключ (≠ `SECRET_KEY`) для шифрования токенов интеграций |

---

## 8. Ссылки

| Документ | Путь |
|----------|------|
| Desktop | [`apps/desktop/README.md`](../apps/desktop/README.md) |
| Web (тесты / Query) | [`apps/web/README.md`](../apps/web/README.md) |
| Apps | [`apps/README.md`](../apps/README.md) |
| WSL fix | [`scripts/enable-wsl.ps1`](../scripts/enable-wsl.ps1) |
| Start local | [`scripts/start-local.ps1`](../scripts/start-local.ps1) |

### Frontend unit / e2e

```powershell
cd apps\web
npm test                 # Vitest
npm run test:e2e         # Playwright login (API + web must be up)
```

### API security regression

```powershell
cd apps\api
.\.venv\Scripts\python -m pytest tests\test_security.py -q
```

---

*FleetPilot · Runbook · v1.3*
