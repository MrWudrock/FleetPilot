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
| `FORMSPREE_ID` | `xyzabc` | Formspree для формы |
| `FORM_SUBMIT_EMAIL` | `leads@domain.ru` | FormSubmit (альтернатива) |
| `YANDEX_METRIKA_ID` | `12345678` | Яндекс.Метрика |
| `GA4_MEASUREMENT_ID` | `G-XXXXXXXX` | Google Analytics 4 |

8. Deploy

**URLs после деплоя:**
- `/` — landing
- `/wireframes` — прототип MVP
- `/pitch-deck` — pitch deck

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

Production URL: `https://fleetpilot-landing.vercel.app`

---

## Переменные окружения

После добавления env в Vercel Dashboard → **Redeploy** (Deployments → ⋯ → Redeploy).

`generate-config.js` создаёт `config.js` при каждом билде на сервере Vercel.

---

## Проверка после деплоя

- [ ] Главная открывается по HTTPS
- [ ] `/wireframes` — 10 экранов MVP
- [ ] `/pitch-deck` — навигация стрелками
- [ ] Форма ROI отправляется (Formspree / FormSubmit inbox)
- [ ] View Source: `config.js` содержит ваш `formspreeId`

---

## Кастомный домен

Vercel → Project → Settings → Domains → Add `fleetpilot.ru`

---

## Локальный preview (без Node.js)

```powershell
cd landing
.\serve.ps1
# http://localhost:3000
```
