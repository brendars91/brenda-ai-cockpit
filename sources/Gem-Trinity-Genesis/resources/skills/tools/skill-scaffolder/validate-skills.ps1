<#
.SYNOPSIS
    Validate all skills in the Skill Library

.DESCRIPTION
    Scans all SKILL.md files and validates:
    - File existence
    - YAML frontmatter format
    - Required fields (name, description)
    - Name matches directory

.EXAMPLE
    .\validate-skills.ps1
#>

$ErrorActionPreference = "Stop"
$SkillsRoot = Join-Path (Join-Path $PSScriptRoot "..\..") ".agent\skills"
$DocsRoot = Join-Path (Join-Path $PSScriptRoot "..\..") "docs\skills"
$ReportPath = Join-Path $DocsRoot "VALIDATION_REPORT.md"

$validCount = 0
$errorCount = 0
$warnings = @()
$errors = @()

Write-Host "Validating skills in: $SkillsRoot" -ForegroundColor Cyan
Write-Host ""

# Find all SKILL.md files
$skillFiles = Get-ChildItem -Path $SkillsRoot -Filter "SKILL.md" -Recurse

foreach ($file in $skillFiles) {
    $skillDir = $file.Directory.Name
    $relativePath = $file.FullName.Replace((Resolve-Path $SkillsRoot).Path, "").TrimStart("\")
    
    Write-Host "Checking: $relativePath" -ForegroundColor Gray
    
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $isValid = $true
    
    # Normalize line endings
    $content = $content -replace "`r`n", "`n"
    $content = $content -replace "`r", "`n"
    
    # Check YAML frontmatter exists (more flexible regex)
    if ($content -match "(?s)^---\s*\n(.+?)\n---") {
        $frontmatter = $Matches[1]
        
        # Check name field
        if ($frontmatter -match "(?m)^name:\s*[`"']?([^`"'\n]+)[`"']?") {
            $skillName = $Matches[1].Trim()
            
            # Check name matches directory (warning only)
            if ($skillName -ne $skillDir) {
                $warnings += "[$relativePath] Name '$skillName' does not match directory '$skillDir'"
            }
        } else {
            $errors += "[$relativePath] Missing 'name' field in frontmatter"
            $isValid = $false
        }
        
        # Check description field
        if ($frontmatter -match "(?m)^description:\s*[`"']?(.+?)[`"']?\s*$") {
            $description = $Matches[1].Trim()
            if ($description.Length -lt 15) {
                $warnings += "[$relativePath] Description is very short (< 15 chars)"
            }
        } else {
            $errors += "[$relativePath] Missing 'description' field in frontmatter"
            $isValid = $false
        }
    } else {
        $errors += "[$relativePath] Missing or invalid YAML frontmatter"
        $isValid = $false
    }
    
    if ($isValid) {
        $validCount++
        Write-Host "  OK" -ForegroundColor Green
    } else {
        $errorCount++
        Write-Host "  ERRORS" -ForegroundColor Red
    }
}

# Generate report
$date = Get-Date -Format "yyyy-MM-dd HH:mm"
$report = @"
# Skill Validation Report

**Generated**: $date
**Skills Root**: ``$SkillsRoot``

## Summary

| Metric | Count |
|--------|-------|
| Total Skills | $($skillFiles.Count) |
| Valid | $validCount |
| With Errors | $errorCount |
| Warnings | $($warnings.Count) |

## Errors

"@

if ($errors.Count -eq 0) {
    $report += "No errors found.`n"
} else {
    foreach ($err in $errors) {
        $report += "- ❌ $err`n"
    }
}

$report += @"

## Warnings

"@

if ($warnings.Count -eq 0) {
    $report += "No warnings.`n"
} else {
    foreach ($warn in $warnings) {
        $report += "- ⚠️ $warn`n"
    }
}

# Save report
$report | Out-File -FilePath $ReportPath -Encoding utf8

Write-Host ""
Write-Host "=== Validation Complete ===" -ForegroundColor Cyan
Write-Host "Total: $($skillFiles.Count) | Valid: $validCount | Errors: $errorCount | Warnings: $($warnings.Count)"
Write-Host "Report saved to: $ReportPath" -ForegroundColor Green

if ($errorCount -gt 0) {
    exit 1
}
