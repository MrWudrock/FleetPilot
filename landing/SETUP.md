# FleetPilot Landing — настройка

## Локальный preview

```powershell
cd landing
.\serve.ps1
# http://localhost:3000
```

Node.js не нужен — используется Python `http.server`.

## Форма заявки

1. `copy config.example.js config.js`
2. Заполните:
   - `formspreeId` — https://formspree.io (бесплатно)
   - или `formSubmitEmail` — https://formsubmit.co

## Vercel

См. [`VERCEL-DEPLOY.md`](VERCEL-DEPLOY.md)

Перед деплоем:

```powershell
.\sync-assets.ps1
```

## Страницы

| URL | Файл |
|-----|------|
| `/` | index.html |
| `/wireframes` | wireframes/index.html |
| `/pitch-deck` | pitch-deck.html |
