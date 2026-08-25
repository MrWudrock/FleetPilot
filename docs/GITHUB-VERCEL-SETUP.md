# GitHub + Vercel — первый push и автодеплой

## Шаг 1. Создать репозиторий на GitHub

1. Откройте [github.com/new](https://github.com/new)
2. **Repository name:** `fleetpilot` (или другое имя)
3. **Visibility:** Public или Private
4. **НЕ** ставьте галочки:
   - ❌ Add a README file
   - ❌ Add .gitignore
   - ❌ Choose a license  
   *(файлы уже есть локально)*
5. Нажмите **Create repository**
6. Скопируйте URL репозитория, например:  
   `https://github.com/Slito/fleetpilot.git`

---

## Шаг 2. Push с вашего компьютера

В PowerShell:

```powershell
cd "C:\Users\Wu\develop\startapp log"

# Подставьте свой URL из GitHub
git remote add origin https://github.com/ВАШ-USERNAME/fleetpilot.git

git push -u origin main
```

При первом push GitHub откроет окно **Sign in** (браузер или токен).

**Альтернатива — скрипт:**

```powershell
.\push-github.ps1 -GitHubUser "ВАШ-USERNAME" -RepoName "fleetpilot"
```

---

## Шаг 3. Подключить Vercel (автодеплой)

1. [vercel.com/new](https://vercel.com/new)
2. **Import Git Repository** → выберите `fleetpilot`
3. **Configure Project:**

| Поле | Значение |
|------|----------|
| **Root Directory** | `landing` ← нажать Edit, указать `landing` |
| **Framework Preset** | Other |
| **Build Command** | `node generate-config.js` |
| **Output Directory** | `.` |
| **Install Command** | *(оставить пустым)* |

4. **Environment Variables** (Production):

| Name | Value |
|------|-------|
| `FORMSPREE_ID` | ваш ID с formspree.io |
| `FORM_SUBMIT_EMAIL` | email для FormSubmit *(опционально)* |
| `YANDEX_METRIKA_ID` | номер счётчика *(опционально)* |

5. **Deploy**

---

## Шаг 4. Проверка

После деплоя откройте:

- `https://fleetpilot.ru/` — landing
- `https://fleetpilot.ru/wireframes` — прототип
- `https://fleetpilot.ru/pitch-deck` — pitch deck

Каждый **push в `main`** → Vercel автоматически пересобирает сайт.

---

## Если `git push` просит пароль

GitHub не принимает пароль аккаунта. Варианты:

1. **GitHub CLI:** установите [cli.github.com](https://cli.github.com) → `gh auth login`
2. **Personal Access Token:** GitHub → Settings → Developer settings → Tokens → Generate → при push используйте token вместо пароля
3. **SSH:** добавьте SSH key в GitHub → remote `git@github.com:USER/fleetpilot.git`

---

## Полезные команды

```powershell
git remote -v              # проверить remote
git status                 # состояние
git push                   # отправить новые коммиты
```

Подробнее по Vercel: [`landing/VERCEL-DEPLOY.md`](../landing/VERCEL-DEPLOY.md)
