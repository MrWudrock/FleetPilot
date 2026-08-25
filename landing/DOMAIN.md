# Домен fleetpilot.ru — настройка

Production URL: **https://fleetpilot.ru**

---

## 1. Vercel — привязка домена

1. [vercel.com](https://vercel.com) → проект **fleetpilot-landing** (или ваш)
2. **Settings** → **Domains**
3. **Add** → `fleetpilot.ru` → **Add**
4. **Add** → `www.fleetpilot.ru` → redirect to `fleetpilot.ru` (Vercel предложит автоматически)

После добавления Vercel покажет **DNS Records** — используйте их на шаге 2.

---

## 2. DNS у регистратора (REG.RU, Nic.ru и др.)

Типичная конфигурация для Vercel:

| Тип | Имя | Значение |
|-----|-----|----------|
| **A** | `@` | `76.76.21.21` |
| **CNAME** | `www` | `cname.vercel-dns.com` |

> **Важно:** не используйте `216.198.79.1` — с российских провайдеров (Obit, REG.RU) этот IP часто **недоступен** (таймаут). Правильный A-запись для Vercel: **`76.76.21.21`**.

Проверка с вашего ПК:

```powershell
nslookup fleetpilot.ru
Test-NetConnection 76.76.21.21 -Port 443   # должно быть True
Test-NetConnection 216.198.79.1 -Port 443  # часто False из РФ
```

> Точные значения смотрите в Vercel → Domains → fleetpilot.ru → **DNS Records** (могут отличаться).

Проверка (через 5–60 мин после сохранения DNS):

```powershell
nslookup fleetpilot.ru
nslookup www.fleetpilot.ru
```

---

## 3. Переменные окружения Vercel

**Settings** → **Environment Variables** → Production:

| Variable | Value |
|----------|-------|
| `SITE_URL` | `https://fleetpilot.ru` |
| `SUPPORT_EMAIL` | `hello@fleetpilot.ru` |
| `FORM_SUBMIT_EMAIL` | `hello@fleetpilot.ru` |
| `FORMSPREE_ID` | ваш ID |
| `YANDEX_METRIKA_ID` | счётчик |

**Redeploy** после изменения env.

---

## 4. Email hello@fleetpilot.ru

Варианты:

| Сервис | Назначение |
|--------|------------|
| **Yandex 360 / Mail.ru для домена** | Полноценная почта |
| **FormSubmit / Formspree** | Только заявки с лендинга (уже настроено в form.js) |
| **Cloudflare Email Routing** | Forward на личный ящик |

Для FormSubmit: подтвердите `hello@fleetpilot.ru` на [formsubmit.co](https://formsubmit.co).

---

## 5. SSL

Vercel выпускает **Let's Encrypt** автоматически после верификации DNS.  
Статус: Domains → **Valid Configuration** ✓

---

## 6. Страницы на домене

| URL | Страница |
|-----|----------|
| https://fleetpilot.ru/ | Landing |
| https://fleetpilot.ru/wireframes/ | MVP прототип |
| https://fleetpilot.ru/pitch-deck | Pitch deck |
| https://fleetpilot.ru/sitemap.xml | Sitemap |
| https://fleetpilot.ru/robots.txt | Robots |

Редирект **www → apex** настроен в `vercel.json`.

---

## 7. Formspree (опционально)

Formspree → Settings → **Allowed Domains** → добавьте:

- `fleetpilot.ru`
- `www.fleetpilot.ru`

---

*FleetPilot · fleetpilot.ru · v1.0*
