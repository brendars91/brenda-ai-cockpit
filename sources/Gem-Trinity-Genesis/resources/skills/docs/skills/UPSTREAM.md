# Upstream Skills Repository

## Source
- **URL**: https://github.com/anthropics/skills
- **Cloned to**: `vendor/anthropics-skills`
- **Clone date**: 2026-01-15
- **Commit hash**: `69c0b1a0674149f27b61b2635f935524b6add202`

## How to Update

```powershell
cd "C:\Users\ASUS\.gemini\Skills proyectos\vendor\anthropics-skills"
git pull
```

After updating, re-run:
1. `validate-skills.ps1` - Verify skill structure
2. `build-catalog.ps1` - Rebuild local catalog

## Consumed Paths

Skills are copied from:
```
vendor/anthropics-skills/skills/<skill-name>/
```

Template available at:
```
vendor/anthropics-skills/template/SKILL.md
```

## Important Notes

- **READ-ONLY**: Do not modify files inside `vendor/anthropics-skills/`
- **COPY ONLY**: When importing skills, copy them to `.agent/skills/by-domain/`
- **Track origin**: Always record `upstream_source` in the skill metadata
