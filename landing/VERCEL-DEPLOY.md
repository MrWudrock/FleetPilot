# Deploy FleetPilot landing на Vercel

## Структура деплоя

```
landing/
├── index.html          # главная
├── pitch-deck.html     # pitch deck (12 слайдов)
├── wireframes/         # MVP прототип
├── vercel.json         # конфиг Vercel
├── generate-config.js  # билд config.js из env
└── deploy.ps1          # CLI деплой
```

Перед деплоем синхронизируйте wireframes:

```powershell
cd "C:\Users\Wu\develop\startapp log\landing"
.\sync-assets.ps1
```

---

## Способ 1 — Vercel Dashboard + GitHub (рекомендуется, Node.js локально не нужен)

1. Создайте репозиторий на GitHub и push проекта
2. [vercel.com/new](https://vercel.com/new) → Import repository
3. **Root Directory:** `landing`
4. **Build Command:** `node generate-config.js`
5. **Output Directory:** `.` (точка)
6. **Install Command:** оставьте пустым
7. Environment Variables (Production):

| Variable | Пример | Назначение |
|----------|--------|------------|
| `SITE_URL` | `https://fleetpilot.ru` | Canonical URL |
| `SUPPORT_EMAIL` | `hello@fleetpilot.ru` | Email поддержки |
| `FORMSPREE_ID` | `xyzabc` | Formspree для формы |
| `FORM_SUBMIT_EMAIL` | `hello@fleetpilot.ru` | FormSubmit |
| `YANDEX_METRIKA_ID` | `12345678` | Яндекс.Метрика |
| `GA4_MEASUREMENT_ID` | `G-XXXXXXXX` | Google Analytics 4 |

8. Deploy

**URLs после деплоя:**
- https://fleetpilot.ru/ — landing
- https://fleetpilot.ru/wireframes — прототип MVP
- https://fleetpilot.ru/pitch-deck — pitch deck

---

## Способ 2 — CLI (нужен Node.js)

```powershell
# Установка Node.js LTS: https://nodejs.org
cd "C:\Users\Wu\develop\startapp log\landing"
.\sync-assets.ps1
.\deploy.ps1
```

При первом деплое:
- **Project name:** `fleetpilot-landing`
- **Directory:** `./`

Production URL: `https://fleetpilot.ru` (после привязки домена) или `https://fleetpilot-landing.vercel.app`

---

## Переменные окружения

После добавления env в Vercel Dashboard → **Redeploy** (Deployments → ⋯ → Redeploy).

`generate-config.js` создаёт `config.js` при каждом билде на сервере Vercel.

---

## Проверка после деплоя

- [ ] https://fleetpilot.ru открывается по HTTPS
- [ ] `/wireframes` — 10 экранов MVP
- [ ] `/pitch-deck` — навигация стрелками
- [ ] Форма ROI отправляется (Formspree / FormSubmit inbox)
- [ ] View Source: `config.js` содержит ваш `formspreeId`

---

## Кастомный домен — fleetpilot.ru

**Полная инструкция:** [`DOMAIN.md`](DOMAIN.md)

1. Vercel → Project → **Settings** → **Domains** → Add `fleetpilot.ru` и `www.fleetpilot.ru`
2. DNS у регистратора:
   - **A** `@` → `76.76.21.21`
   - **CNAME** `www` → `cname.vercel-dns.com`
3. Env: `SITE_URL=https://fleetpilot.ru`, `SUPPORT_EMAIL=hello@fleetpilot.ru`
4. Redeploy

Production: **https://fleetpilot.ru**

---

## Локальный preview (без Node.js)

```powershell
cd landing
.\serve.ps1
# http://localhost:3000
```
