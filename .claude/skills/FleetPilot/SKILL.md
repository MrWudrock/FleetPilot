---
name: fleetpilot-conventions
description: Development conventions and patterns for FleetPilot. Python project with conventional commits.
---

# Fleetpilot Conventions

> Generated from [MrWudrock/FleetPilot](https://github.com/MrWudrock/FleetPilot) on 2026-08-25

## Overview

This skill teaches Claude the development patterns and conventions used in FleetPilot.

## Tech Stack

- **Primary Language**: Python
- **Architecture**: type-based module organization
- **Test Location**: mixed
- **Test Framework**: vitest

## When to Use This Skill

Activate this skill when:
- Making changes to this repository
- Adding new features following established patterns
- Writing tests that match project conventions
- Creating commits with proper message format

## Commit Conventions

Follow these commit message conventions based on 10 analyzed commits.

### Commit Style: Conventional Commits

### Prefixes Used

- `feat`
- `docs`
- `chore`

### Message Guidelines

- Average message length: ~67 characters
- Keep first line concise and descriptive
- Use imperative mood ("Add feature" not "Added feature")


*Commit message example*

```text
chore: extend gitignore and add root npm scripts
```

*Commit message example*

```text
feat(api): add FleetPilot FastAPI backend with multi-tenant auth and fleet ops
```

*Commit message example*

```text
docs: add runbooks, MVP guides, and architecture updates
```

*Commit message example*

```text
feat(web): add Next.js dashboard with TanStack Query and auth flows
```

*Commit message example*

```text
feat(agents): add route, dispatch, fuel, maintenance, permit agent templates
```

*Commit message example*

```text
feat(desktop): add Electron shell for Windows pilot installs
```

*Commit message example*

```text
feat(infra): add Docker Compose stack, local scripts, and GitHub Actions CI
```

*Commit message example*

```text
feat(scan): add interactive architecture map (Foglamp Scan style)
```

## Architecture

### Project Structure: Monorepo

This project uses **type-based** module organization.

### Configuration Files

- `.github/workflows/app-ci.yml`
- `.github/workflows/deploy.yml`
- `.github/workflows/preview.yml`
- `apps/api/Dockerfile`
- `apps/desktop/package.json`
- `apps/web/Dockerfile`
- `apps/web/next.config.ts`
- `apps/web/package.json`
- `apps/web/playwright.config.ts`
- `apps/web/tailwind.config.ts`
- `apps/web/tsconfig.json`
- `apps/web/vitest.config.ts`
- `docker-compose.yml`
- `landing/vercel.json`
- `package.json`

### Guidelines

- Group code by type (components, services, utils)
- Keep related functionality in the same type folder
- Avoid circular dependencies between type folders

## Code Style

### Language: Python

### Naming Conventions

| Element | Convention |
|---------|------------|
| Files | camelCase |
| Functions | camelCase |
| Classes | PascalCase |
| Constants | SCREAMING_SNAKE_CASE |

### Import Style: Path Aliases (@/, ~/)

### Export Style: Default Exports


*Preferred import style*

```typescript
// Use path aliases for imports
import { Button } from '@/components/Button'
import { useAuth } from '@/hooks/useAuth'
import { api } from '@/lib/api'
```

*Preferred export style*

```typescript
// Use default exports for main component/function
export default function UserProfile() { ... }
```

## Testing

### Test Framework: vitest

### File Pattern: `*.test.ts`

### Test Types

- **Unit tests**: Test individual functions and components in isolation
- **E2e tests**: Test complete user flows through the application


*Test file structure*

```typescript
import { describe, it, expect } from 'vitest'

describe('MyFunction', () => {
  it('should return expected result', () => {
    const result = myFunction(input)
    expect(result).toBe(expected)
  })
})
```

## Error Handling

### Error Handling Style: Try-Catch Blocks


*Standard error handling pattern*

```typescript
try {
  const result = await riskyOperation()
  return result
} catch (error) {
  console.error('Operation failed:', error)
  throw new Error('User-friendly message')
}
```

## Common Workflows

These workflows were detected from analyzing commit patterns.

### Feature Development

Standard feature implementation workflow

**Frequency**: ~27 times per month

**Steps**:
1. Add feature implementation
2. Add tests for feature
3. Update documentation

**Files typically involved**:
- `apps/web/e2e/*`
- `apps/web/*`
- `apps/web/src/app/accept-invite/*`
- `**/*.test.*`
- `**/api/**`

**Example commit sequence**:
```
chore: extend gitignore and add root npm scripts
feat(api): add FleetPilot FastAPI backend with multi-tenant auth and fleet ops
feat(web): add Next.js dashboard with TanStack Query and auth flows
```


## Best Practices

Based on analysis of the codebase, follow these practices:

### Do

- Use conventional commit format (feat:, fix:, etc.)
- Write tests using vitest
- Follow *.test.ts naming pattern
- Use camelCase for file names
- Prefer default exports

### Don't

- Don't use long relative imports (use aliases)
- Don't write vague commit messages
- Don't skip tests for new features
- Don't deviate from established patterns without discussion

---

*This skill was auto-generated by [ECC Tools](https://ecc.tools). Review and customize as needed for your team.*
