# PowerShell Update Script for Centre-colorBot
# This script handles the update process

param(
    [string]$UpdateUrl = "",
    [string]$BackupDir = "backup"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Centre-colorBot Update Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Warning: Not running as administrator. Some operations may fail." -ForegroundColor Yellow
}

# Create backup directory
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
    Write-Host "Created backup directory: $BackupDir" -ForegroundColor Green
}

# Backup important files
Write-Host "Backing up configuration files..." -ForegroundColor Yellow
$filesToBackup = @("config.json", "version.json")
foreach ($file in $filesToBackup) {
    if (Test-Path $file) {
        $backupPath = Join-Path $BackupDir "$file.backup"
        Copy-Item $file $backupPath -Force
        Write-Host "  Backed up: $file" -ForegroundColor Gray
    }
}

# If update URL is provided, download update
if ($UpdateUrl -ne "") {
    Write-Host ""
    Write-Host "Downloading update from: $UpdateUrl" -ForegroundColor Yellow
    
    $updateZip = Join-Path $ScriptDir "update.zip"
    try {
        Invoke-WebRequest -Uri $UpdateUrl -OutFile $updateZip -UseBasicParsing
        Write-Host "Download completed." -ForegroundColor Green
        
        # Extract update
        Write-Host "Extracting update..." -ForegroundColor Yellow
        Expand-Archive -Path $updateZip -DestinationPath $ScriptDir -Force
        Remove-Item $updateZip -Force
        Write-Host "Update extracted successfully." -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to download update: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Update process completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
