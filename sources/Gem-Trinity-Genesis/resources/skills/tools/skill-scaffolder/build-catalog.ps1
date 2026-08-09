<#
.SYNOPSIS
    Build the skills catalog from all SKILL.md files

.DESCRIPTION
    Scans all skills and generates docs/skills/CATALOG.md with:
    - scope (core, by-domain, projects)
    - domain
    - name
    - description
    - path
    - upstream_source (if applicable)

.EXAMPLE
    .\build-catalog.ps1
#>

$ErrorActionPreference = "Stop"
$SkillsRoot = Join-Path (Join-Path $PSScriptRoot "..\..") ".agent\skills"
$DocsRoot = Join-Path (Join-Path $PSScriptRoot "..\..") "docs\skills"
$CatalogPath = Join-Path $DocsRoot "CATALOG.md"

Write-Host "Building catalog from: $SkillsRoot" -ForegroundColor Cyan

$skills = @()

# Find all SKILL.md files
$skillFiles = Get-ChildItem -Path $SkillsRoot -Filter "SKILL.md" -Recurse

foreach ($file in $skillFiles) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $relativePath = $file.FullName.Replace((Resolve-Path $SkillsRoot).Path, "").TrimStart("\")
    
    # Normalize line endings
    $content = $content -replace "`r`n", "`n"
    $content = $content -replace "`r", "`n"
    
    # Parse frontmatter
    if ($content -match "(?s)^---\s*\n(.+?)\n---") {
        $frontmatter = $Matches[1]
        
        $name = if ($frontmatter -match "(?m)^name:\s*[`"']?([^`"'\n]+)[`"']?") { $Matches[1].Trim() } else { "unknown" }
        $description = if ($frontmatter -match "(?m)^description:\s*[`"']?(.+?)[`"']?\s*$") { $Matches[1].Trim() } else { "No description" }
        
        # Truncate description
        if ($description.Length -gt 80) {
            $description = $description.Substring(0, 77) + "..."
        }
        
        # Determine scope and domain from path
        $pathParts = $relativePath -split "\\"
        $scope = $pathParts[0]
        
        $domain = switch ($scope) {
            "_core" { "-" }
            "by-domain" { if ($pathParts.Count -gt 1) { $pathParts[1] } else { "_inbox" } }
            "projects" { if ($pathParts.Count -gt 2) { $pathParts[2] } else { "-" } }
            default { "-" }
        }
        
        # Check for upstream source in content
        $upstreamSource = ""
        if ($content -match "upstream_source:\s*(.+)") {
            $upstreamSource = $Matches[1].Trim()
        }
        
        $skills += [PSCustomObject]@{
            Scope = $scope
            Domain = $domain
            Name = $name
            Description = $description
            Path = $relativePath
            UpstreamSource = $upstreamSource
        }
    }
}

# Sort skills
$skills = $skills | Sort-Object Scope, Domain, Name

# Generate catalog
$date = Get-Date -Format "yyyy-MM-dd HH:mm"
$catalog = @"
# Skills Catalog

**Generated**: $date
**Total Skills**: $($skills.Count)

## Quick Reference

| Scope | Domain | Name | Description |
|-------|--------|------|-------------|
"@

foreach ($skill in $skills) {
    $catalog += "| $($skill.Scope) | $($skill.Domain) | **$($skill.Name)** | $($skill.Description) |`n"
}

# Group by scope
$catalog += @"

## By Scope

"@

$byScope = $skills | Group-Object Scope
foreach ($group in $byScope) {
    $catalog += "### $($group.Name)`n`n"
    
    foreach ($skill in $group.Group) {
        $catalog += "- **$($skill.Name)** ($($skill.Domain)): $($skill.Description)`n"
    }
    
    $catalog += "`n"
}

# Save catalog
$catalog | Out-File -FilePath $CatalogPath -Encoding utf8

Write-Host ""
Write-Host "=== Catalog Built ===" -ForegroundColor Cyan
Write-Host "Total skills: $($skills.Count)"
Write-Host "Saved to: $CatalogPath" -ForegroundColor Green
