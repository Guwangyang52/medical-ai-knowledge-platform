param(
    [string]$Root = ""
)

$ErrorActionPreference = "Stop"

function Resolve-Root {
    param([string]$InputRoot)
    if ([string]::IsNullOrWhiteSpace($InputRoot)) {
        $InputRoot = Read-Host "Install directory, for example <YOUR_INSTALL_DIR>"
    }
    if ([string]::IsNullOrWhiteSpace($InputRoot)) {
        throw "Install directory cannot be empty."
    }
    return [System.IO.Path]::GetFullPath($InputRoot)
}

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$InstallRoot = Resolve-Root $Root

$VaultPath = Join-Path $InstallRoot "my-vault"
$ExecutionPath = Join-Path $InstallRoot "execution-platform"
$PlatformCorePath = Join-Path $ExecutionPath "platform-core"
$ProjectsPath = Join-Path $ExecutionPath "projects"
$LogsPath = Join-Path $ExecutionPath "logs"
$OutputsPath = Join-Path $ExecutionPath "outputs"
$ExecutionConfigPath = Join-Path $ExecutionPath "config"
$SkillsPath = Join-Path $InstallRoot "my-skills"

New-Item -ItemType Directory -Path $InstallRoot -Force | Out-Null
New-Item -ItemType Directory -Path $ExecutionPath,$ProjectsPath,$LogsPath,$OutputsPath,$ExecutionConfigPath,$SkillsPath -Force | Out-Null

Copy-Item -Path (Join-Path $RepoRoot "starter-vault") -Destination $VaultPath -Recurse -Force
Copy-Item -Path (Join-Path $RepoRoot "platform-core") -Destination $PlatformCorePath -Recurse -Force
Copy-Item -Path (Join-Path $RepoRoot "starter-skills\*") -Destination $SkillsPath -Recurse -Force
Copy-Item -Path (Join-Path $RepoRoot "execution-platform-template\*") -Destination $ExecutionPath -Recurse -Force

$Rscript = "Rscript"
$FoundRscript = Get-Command Rscript -ErrorAction SilentlyContinue
if ($FoundRscript) {
    $Rscript = $FoundRscript.Source
}

$PathsYaml = @"
platform_root: "$($InstallRoot.Replace('\', '\\'))"
vault_path: "$($VaultPath.Replace('\', '\\'))"
execution_platform: "$($ExecutionPath.Replace('\', '\\'))"

knowledge:
  index: "$((Join-Path $VaultPath 'wiki\index.md').Replace('\', '\\'))"
  analyses: "$((Join-Path $VaultPath 'wiki\analyses').Replace('\', '\\'))"
  concepts: "$((Join-Path $VaultPath 'wiki\concepts').Replace('\', '\\'))"
  sources: "$((Join-Path $VaultPath 'wiki\sources').Replace('\', '\\'))"

execution:
  projects: "$($ProjectsPath.Replace('\', '\\'))"
  outputs: "$($OutputsPath.Replace('\', '\\'))"
  logs: "$($LogsPath.Replace('\', '\\'))"

runtime:
  python_path: ""
  rscript_path: "$($Rscript.Replace('\', '\\'))"
"@

$LocalConfigPath = Join-Path $ExecutionConfigPath "paths.yaml"
$PathsYaml | Set-Content -Path $LocalConfigPath -Encoding UTF8

$WorkspacePath = Join-Path $InstallRoot "workspace.code-workspace"
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
$WorkspaceJson | Set-Content -Path $WorkspacePath -Encoding UTF8

Write-Host ""
Write-Host "Initialized platform at:" $InstallRoot
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Open workspace.code-workspace"
Write-Host "2. Ask your AI agent to read my-vault\CLAUDE.md or my-vault\AGENTS.md"
Write-Host "3. Run the search example:"
Write-Host "   python `"$PlatformCorePath\scripts\search_kb.py`" `"continuous meta analysis`""
Write-Host "4. Run Python tasks with:"
Write-Host "   python `"$PlatformCorePath\scripts\run_python_task.py`" `".\projects\<task>`" --script `"src/analysis.py`""
Write-Host ""
if (-not $FoundRscript) {
    Write-Host "Note: Rscript was not found in PATH. Edit runtime.rscript_path in config\paths.yaml before running R tasks."
}
