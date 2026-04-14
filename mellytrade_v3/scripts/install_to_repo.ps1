param(
  [string]$RepoPath = ".",
  [string]$SourcePath = "./MellyTrade_v3"
)

$ErrorActionPreference = "Stop"
Write-Host "Installing MellyTrade v3 into repo: $RepoPath"

if (!(Test-Path $RepoPath)) { throw "Repo path not found: $RepoPath" }
if (!(Test-Path $SourcePath)) { throw "Source path not found: $SourcePath" }

$folders = @("mellytrade-api", "mellytrade", "mt5", ".github")
foreach ($folder in $folders) {
  $src = Join-Path $SourcePath $folder
  if (Test-Path $src) {
    Copy-Item $src -Destination $RepoPath -Recurse -Force
  }
}
Copy-Item (Join-Path $SourcePath ".env.example") -Destination $RepoPath -Force
Copy-Item (Join-Path $SourcePath "README.md") -Destination (Join-Path $RepoPath "README_MellyTrade_v3.md") -Force

Push-Location $RepoPath
if (Test-Path ".git") {
  git add .
  git status --short
  Write-Host "Files installed and staged."
} else {
  Write-Host "Installed, but this is not a git repo."
}
Pop-Location
