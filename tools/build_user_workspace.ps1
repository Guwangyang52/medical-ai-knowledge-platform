param(
    [string]$Version = "",
    [string]$OutputDir = ""
)

$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    return [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
}

function Copy-Directory {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        throw "Source directory not found: $Source"
    }
    Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
}

function Write-Utf8File {
    param(
        [string]$Path,
        [string]$Content
    )

    $Utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($Path, $Content, $Utf8NoBom)
}

$RepoRoot = Get-RepoRoot

if ([string]::IsNullOrWhiteSpace($Version)) {
    $Version = "0.1.0"
}
$Version = $Version.TrimStart("v")

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $RepoRoot "dist"
}
$OutputDir = [System.IO.Path]::GetFullPath($OutputDir)

$WorkspaceName = "MedicalAIKnowledgeWorkspace"
$WorkspaceDir = Join-Path $OutputDir $WorkspaceName
$ZipPath = Join-Path $OutputDir "MedicalAIKnowledgeWorkspace-v$Version.zip"
$UserReadmeName = "README_" + [char]0x5148 + [char]0x6253 + [char]0x5F00 + [char]0x6211 + ".md"

if (Test-Path -LiteralPath $WorkspaceDir) {
    Remove-Item -LiteralPath $WorkspaceDir -Recurse -Force
}
if (Test-Path -LiteralPath $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}

New-Item -ItemType Directory -Path $WorkspaceDir | Out-Null

$VaultPath = Join-Path $WorkspaceDir "my-vault"
$ExecutionPath = Join-Path $WorkspaceDir "execution-platform"
$SkillsPath = Join-Path $WorkspaceDir "my-skills"
$ConfigPath = Join-Path $ExecutionPath "config"

Copy-Directory -Source (Join-Path $RepoRoot "starter-vault") -Destination $VaultPath
Copy-Directory -Source (Join-Path $RepoRoot "starter-skills") -Destination $SkillsPath
Copy-Directory -Source (Join-Path $RepoRoot "execution-platform-template") -Destination $ExecutionPath
Copy-Directory -Source (Join-Path $RepoRoot "platform-core") -Destination (Join-Path $ExecutionPath "platform-core")

New-Item -ItemType Directory -Path (Join-Path $ExecutionPath "projects") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $ExecutionPath "logs") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $ExecutionPath "outputs") -Force | Out-Null
New-Item -ItemType Directory -Path $ConfigPath -Force | Out-Null

$PathsYaml = @"
platform_root: "../.."
vault_path: "../../my-vault"
execution_platform: ".."

knowledge:
  index: "../../my-vault/wiki/index.md"
  analyses: "../../my-vault/wiki/analyses"
  concepts: "../../my-vault/wiki/concepts"
  sources: "../../my-vault/wiki/sources"

execution:
  projects: "../projects"
  outputs: "../outputs"
  logs: "../logs"

runtime:
  python_path: ""
  rscript_path: "Rscript"
"@
Write-Utf8File -Path (Join-Path $ConfigPath "paths.yaml") -Content $PathsYaml

$WorkspaceJson = @"
{
  "folders": [
    {
      "name": "my-vault",
      "path": "my-vault"
    },
    {
      "name": "execution-platform",
      "path": "execution-platform"
    },
    {
      "name": "my-skills",
      "path": "my-skills"
    }
  ],
  "settings": {
    "files.encoding": "utf8"
  }
}
"@
Write-Utf8File -Path (Join-Path $WorkspaceDir "workspace.code-workspace") -Content $WorkspaceJson

$StartScript = @'
$Workspace = Join-Path $PSScriptRoot "workspace.code-workspace"
if (-not (Test-Path -LiteralPath $Workspace)) {
    throw "workspace.code-workspace not found: $Workspace"
}
code $Workspace
'@
Write-Utf8File -Path (Join-Path $WorkspaceDir "start.ps1") -Content $StartScript

$UserReadmeTemplate = Join-Path $RepoRoot "templates\README_user_workspace_zh-CN.md"
if (-not (Test-Path -LiteralPath $UserReadmeTemplate)) {
    throw "User README template not found: $UserReadmeTemplate"
}
Copy-Item -LiteralPath $UserReadmeTemplate -Destination (Join-Path $WorkspaceDir $UserReadmeName) -Force

Compress-Archive -Path $WorkspaceDir -DestinationPath $ZipPath -Force

Write-Host "Built user workspace:"
Write-Host "  $WorkspaceDir"
Write-Host "Built release zip:"
Write-Host "  $ZipPath"
