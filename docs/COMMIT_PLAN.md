# FleetPilot — план коммитов (working tree → main)

> **Контекст:** на `main` нет коммитов поверх `origin/main`; ~230 файлов в working tree.  
> Порядок ниже минимизирует конфликты и даёт reviewable PR-ы.

---

## Commit 1 — `chore: gitignore and repo scaffolding`

**Цель:** подготовить репозиторий, не таща бинарники и секреты.

```
.gitignore
package.json                    # root npm scripts (scan, dev:web)
.linear.env.example
```

**Не коммитить:** PDF, xlsx, `Screenshot_*.png`, `crm.txt`, `*.docx`, `landing/downloads/*.exe`.

**Команды:**
```powershell
git add .gitignore package.json .linear.env.example
git commit -m "chore: extend gitignore and add root npm scripts"
```

---

## Commit 2 — `feat(api): FastAPI backend with auth, fleet, ops, permit`

**Цель:** самодостаточный API-слой.

```
apps/api/
  app/
  alembic/
  tests/
  scripts/
  requirements.txt
  Dockerfile
  entrypoint.sh
  alembic.ini
  .dockerignore
  .env.example          # NEW — env template
```

**Команды:**
```powershell
git add apps/api/
git commit -m "feat(api): add FleetPilot FastAPI backend with multi-tenant auth and fleet ops"
```

---

## Commit 3 — `feat(web): Next.js operator dashboard`

```
apps/web/
  src/
  e2e/
  package.json
  package-lock.json
  Dockerfile
  ...
```

```powershell
git add apps/web/
git commit -m "feat(web): add Next.js dashboard with TanStack Query and auth flows"
```

---

## Commit 4 — `feat(desktop): Electron Windows client`

```
apps/desktop/
apps/README.md
```

```powershell
git add apps/desktop/ apps/README.md
git commit -m "feat(desktop): add Electron shell for Windows pilot installs"
```

---

## Commit 5 — `feat(agents): AI agent templates`

```
agents/
```

```powershell
git add agents/
git commit -m "feat(agents): add route, dispatch, fuel, maintenance, permit agent templates"
```

---

## Commit 6 — `feat(infra): Docker Compose, dev scripts, CI`

```
docker-compose.yml
dev.ps1
seed-demo.ps1
serve.ps1
scripts/
.github/workflows/
```

```powershell
git add docker-compose.yml dev.ps1 seed-demo.ps1 serve.ps1 scripts/ .github/
git commit -m "feat(infra): add Docker Compose stack, local scripts, and GitHub Actions CI"
```

---

## Commit 7 — `feat(scan): interactive codebase graph explorer`

```
scan/
```

```powershell
git add scan/
git commit -m "feat(scan): add interactive architecture map (Foglamp Scan style)"
```

**Примечание:** `scan/data/graph.json` — генерируемый; либо коммитить после `python scan/build_graph.py`, либо добавить в `.gitignore` и генерировать в CI.

---

## Commit 8 — `docs: runbooks, architecture, fleet-ai guides`

```
docs/IMPLEMENTATION_GUIDE.md
docs/NEXT-STEPS.md
docs/PILOT-TEST-GUIDE.md
docs/RUNBOOK.md
docs/COMMIT_PLAN.md
docs/fleet-ai/   # новые и изменённые
```

```powershell
git add docs/
git commit -m "docs: add runbooks, MVP guides, and architecture updates"
```

---

## Commit 9 — `feat(landing): marketing site, legal pages, SEO`

```
landing/
wireframes/
```

```powershell
git add landing/ wireframes/
git commit -m "feat(landing): refresh marketing site with legal pages and desktop download CTA"
```

---

## Commit 10 — `docs: update root README and legacy doc tweaks`

```
README.md
docs/GITHUB-VERCEL-SETUP.md
docs/fleet-ai/JIRA-IMPORT.md
docs/fleet-ai/PRD.md
docs/fleet-ai/architecture.md
docs/fleet-ai/backlog-jira-import.csv
docs/fleet-ai/pitch-deck.html
```

```powershell
git add README.md docs/GITHUB-VERCEL-SETUP.md docs/fleet-ai/JIRA-IMPORT.md docs/fleet-ai/PRD.md docs/fleet-ai/architecture.md docs/fleet-ai/backlog-jira-import.csv docs/fleet-ai/pitch-deck.html
git commit -m "docs: update root README and product documentation for FleetPilot MVP"
```

---

## Commit 11 (optional) — `chore(cursor): workspace rules`

```
.cursor/rules/
```

Отдельно, если команда использует Cursor rules.

---

## Pre-push checklist

- [ ] `cd apps/api && pytest tests/ -q`
- [ ] `cd apps/web && npm test && npm run build`
- [ ] `DEBUG=false` + уникальные `SECRET_KEY` и `CREDENTIALS_ENCRYPTION_KEY` в deploy env
- [ ] `ALLOW_PUBLIC_SIGNUP=false` в production
- [ ] Не поднимать `docker-web` и локальный `npm run dev` одновременно на :3000
- [ ] `.\scripts\start-local.ps1` → health OK на :8800

---

## Альтернатива: один squash PR

Если нужен один PR для pilot:

```powershell
git add -A
# вручную unstage мусор: git reset HEAD -- "*.pdf" "*.xlsx" Screenshot_*
git commit -m "feat: FleetPilot MVP monorepo (api, web, desktop, agents, infra)"
```

Рекомендуется **разбивка 1–10** для code review.
