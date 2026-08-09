<#
.SYNOPSIS
    Skill Scaffolder - Create and adapt skills for the Skill Library

.DESCRIPTION
    Commands:
    - create: Create a new skill from template
    - adapt: Adapt an existing skill for a specific project

.EXAMPLE
    .\skill-scaffolder.ps1 create -Name "my-skill" -Description "My skill description" -Domain "web"
    .\skill-scaffolder.ps1 adapt -SourcePath ".agent\skills\by-domain\web\webapp-testing" -NewName "my-webapp-testing" -ProjectId "project-123"
#>

param(
    [Parameter(Position=0)]
    [ValidateSet("create", "adapt")]
    [string]$Command,
    
    # Create parameters
    [string]$Name,
    [string]$Description,
    [string]$Domain = "_inbox",
    [ValidateSet("by-domain", "projects")]
    [string]$Scope = "by-domain",
    [string]$ProjectId,
    [string[]]$Tags,
    
    # Adapt parameters
    [string]$SourcePath,
    [string]$NewName,
    [string]$Reason,
    
    # Common
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$SkillsRoot = Join-Path (Join-Path $PSScriptRoot "..\..") ".agent\skills"
$DocsRoot = Join-Path (Join-Path $PSScriptRoot "..\..") "docs\skills"

function Write-SkillFile {
    param(
        [string]$Path,
        [string]$Name,
        [string]$Description,
        [string]$Domain,
        [string]$UpstreamSource = "",
        [string]$AdaptedFrom = "",
        [string]$ProjectId = ""
    )
    
    $date = Get-Date -Format "yyyy-MM-dd"
    $metadata = @()
    
    if ($UpstreamSource) { $metadata += "upstream_source: $UpstreamSource" }
    if ($AdaptedFrom) { $metadata += "adapted_from: $AdaptedFrom" }
    if ($ProjectId) { $metadata += "project_id: $ProjectId" }
    if ($metadata.Count -gt 0) { $metadata += "created_at: $date" }
    
    $metadataSection = ""
    if ($metadata.Count -gt 0) {
        $metadataSection = @"

## Metadata
``````yaml
$($metadata -join "`n")
``````
"@
    }
    
    $content = @"
---
name: $Name
description: $Description
---

# $Name
$metadataSection

## Purpose

[Describe the purpose of this skill]

## When to Use

- [Trigger condition 1]
- [Trigger condition 2]

## Instructions

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Examples

### Example 1
[Provide a usage example]

## References

- [Link to relevant documentation]
"@
    
    if ($DryRun) {
        Write-Host "[DRY-RUN] Would create: $Path" -ForegroundColor Yellow
        Write-Host $content
    } else {
        $dir = Split-Path $Path -Parent
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
        $content | Out-File -FilePath $Path -Encoding utf8
        Write-Host "Created: $Path" -ForegroundColor Green
    }
}

function Add-AdaptationRecord {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$Reason,
        [string]$ProjectId
    )
    
    $adaptationsFile = Join-Path $DocsRoot "ADAPTATIONS.md"
    $date = Get-Date -Format "yyyy-MM-dd"
    
    $record = @"

| $date | ``$Source`` | ``$Destination`` | $ProjectId | $Reason |
"@
    
    if ($DryRun) {
        Write-Host "[DRY-RUN] Would append to ADAPTATIONS.md:" -ForegroundColor Yellow
        Write-Host $record
    } else {
        if (-not (Test-Path $adaptationsFile)) {
            $header = @"
# Skill Adaptations Log

| Date | Source | Destination | Project ID | Reason |
|------|--------|-------------|------------|--------|
"@
            $header | Out-File -FilePath $adaptationsFile -Encoding utf8
        }
        $record | Add-Content -Path $adaptationsFile -Encoding utf8
        Write-Host "Recorded adaptation in ADAPTATIONS.md" -ForegroundColor Green
    }
}

# Main logic
switch ($Command) {
    "create" {
        if (-not $Name) { throw "Name is required for create command" }
        if (-not $Description) { throw "Description is required for create command" }
        if ($Scope -eq "projects" -and -not $ProjectId) { 
            throw "ProjectId is required when Scope is 'projects'" 
        }
        
        # Validate kebab-case
        if ($Name -notmatch "^[a-z0-9]+(-[a-z0-9]+)*$") {
            throw "Name must be kebab-case (e.g., 'my-skill-name')"
        }
        
        # Determine path
        if ($Scope -eq "by-domain") {
            $targetPath = Join-Path $SkillsRoot "by-domain\$Domain\$Name\SKILL.md"
        } else {
            $targetPath = Join-Path $SkillsRoot "projects\$ProjectId\$Domain\$Name\SKILL.md"
        }
        
        # Check if exists
        if ((Test-Path $targetPath) -and -not $DryRun) {
            throw "Skill already exists at: $targetPath"
        }
        
        Write-SkillFile -Path $targetPath -Name $Name -Description $Description -Domain $Domain
        
        # Create optional subdirectories
        $skillDir = Split-Path $targetPath -Parent
        if (-not $DryRun) {
            @("examples", "references", "scripts") | ForEach-Object {
                $subDir = Join-Path $skillDir $_
                if (-not (Test-Path $subDir)) {
                    New-Item -ItemType Directory -Path $subDir -Force | Out-Null
                }
            }
            Write-Host "Created subdirectories: examples/, references/, scripts/" -ForegroundColor Cyan
        }
    }
    
    "adapt" {
        if (-not $SourcePath) { throw "SourcePath is required for adapt command" }
        if (-not $NewName) { throw "NewName is required for adapt command" }
        if (-not $ProjectId) { throw "ProjectId is required for adapt command" }
        if (-not $Reason) { throw "Reason is required for adapt command" }
        
        # Validate source exists
        $sourceSkillFile = Join-Path $SourcePath "SKILL.md"
        if (-not (Test-Path $sourceSkillFile)) {
            throw "Source skill not found: $sourceSkillFile"
        }
        
        # Determine domain from source path
        $pathParts = $SourcePath -split "\\" | Where-Object { $_ }
        $domainIndex = [array]::IndexOf($pathParts, "by-domain")
        $Domain = if ($domainIndex -ge 0 -and $domainIndex + 1 -lt $pathParts.Count) {
            $pathParts[$domainIndex + 1]
        } else {
            "_inbox"
        }
        
        # Target path
        $targetDir = Join-Path $SkillsRoot "projects\$ProjectId\$Domain\$NewName"
        $targetPath = Join-Path $targetDir "SKILL.md"
        
        # Check if exists
        if ((Test-Path $targetPath) -and -not $DryRun) {
            throw "Skill already exists at: $targetPath"
        }
        
        if ($DryRun) {
            Write-Host "[DRY-RUN] Would copy from: $SourcePath" -ForegroundColor Yellow
            Write-Host "[DRY-RUN] Would copy to: $targetDir" -ForegroundColor Yellow
        } else {
            # Copy entire skill directory
            Copy-Item -Path $SourcePath -Destination $targetDir -Recurse
            
            # Update SKILL.md with adaptation info
            $content = Get-Content $targetPath -Raw
            $date = Get-Date -Format "yyyy-MM-dd"
            $adaptSection = @"

## Project-specific Adjustments

> Adapted from: $SourcePath
> Project: $ProjectId
> Date: $date
> Reason: $Reason

[Document project-specific changes here]
"@
            $content = $content -replace "^(---.+?---)", "`$1`n$adaptSection"
            $content | Out-File -FilePath $targetPath -Encoding utf8
            
            Write-Host "Adapted skill to: $targetDir" -ForegroundColor Green
        }
        
        Add-AdaptationRecord -Source $SourcePath -Destination $targetDir -Reason $Reason -ProjectId $ProjectId
    }
    
    default {
        Write-Host @"
Skill Scaffolder - Create and adapt skills

Commands:
  create    Create a new skill from template
  adapt     Adapt an existing skill for a project

Usage:
  .\skill-scaffolder.ps1 create -Name <name> -Description <desc> [-Domain <domain>] [-Scope by-domain|projects] [-ProjectId <id>] [-DryRun]
  .\skill-scaffolder.ps1 adapt -SourcePath <path> -NewName <name> -ProjectId <id> -Reason <reason> [-DryRun]

Examples:
  .\skill-scaffolder.ps1 create -Name "sap-reports" -Description "SAP report generation" -Domain "sap"
  .\skill-scaffolder.ps1 adapt -SourcePath ".agent\skills\by-domain\documents\xlsx" -NewName "sap-xlsx" -ProjectId "sap-fico-2024" -Reason "Custom SAP export format"
"@
    }
}
