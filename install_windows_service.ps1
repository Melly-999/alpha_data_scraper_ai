# Windows Service Installation Script for Trading Bot
# Run as Administrator
# Usage: powershell -ExecutionPolicy Bypass -File install_windows_service.ps1

param(
    [switch]$Uninstall,
    [switch]$Start,
    [switch]$Stop,
    [switch]$Status,
    [string]$ServiceName = "GrokAlphaAI",
    [string]$DisplayName = "Grok Alpha AI Trading Bot",
    [string]$Description = "Automated MT5 trading bot with AI signal generation"
)

# Require administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script requires administrator privileges!" -ForegroundColor Red
    exit 1
}

# Get script location
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = $ScriptPath

# Virtual environment activation
$VenvPath = Join-Path $ProjectRoot ".venv"
if (-not (Test-Path $VenvPath)) {
    Write-Host "Virtual environment not found at $VenvPath" -ForegroundColor Red
    Write-Host "Please create it first: python -m venv .venv"
    exit 1
}

$PythonPath = Join-Path $VenvPath "Scripts\python.exe"
$PipPath = Join-Path $VenvPath "Scripts\pip.exe"

# Function to check if service exists
function Test-ServiceExists {
    param([string]$Name)
    return (Get-Service -Name $Name -ErrorAction SilentlyContinue) -ne $null
}

# Function to install service
function Install-TradingBotService {
    Write-Host "Installing Trading Bot as Windows Service..." -ForegroundColor Cyan
    
    # Check if service already exists
    if (Test-ServiceExists $ServiceName) {
        Write-Host "Service '$ServiceName' already exists. Removing first..." -ForegroundColor Yellow
        Remove-TradingBotService
    }
    
    # Create wrapper script for Python
    $WrapperScript = Join-Path $ProjectRoot "service_wrapper.ps1"
    $WrapperContent = @"
# Service wrapper script for Trading Bot
param([string]`$Action = "run")

`$SleepInterval = 5
`$MaxRetries = 3
`$Retries = 0

try {
    Set-Location "$ProjectRoot"
    
    # Activate virtual environment
    & "$VenvPath\Scripts\Activate.ps1"
    
    # Main service loop
    while (`$true) {
        try {
            Write-Host "[`$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Starting Trading Bot..." -ForegroundColor Green
            & "$PythonPath" example_runner.py `
                --symbols EURUSD GBPUSD USDJPY AUDUSD EURJPY `
                --demo
            
            `$Retries = 0
        }
        catch {
            Write-Host "[`$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Service error: `$_" -ForegroundColor Red
            `$Retries++
            
            if (`$Retries -gt `$MaxRetries) {
                Write-Host "Max retries exceeded. Exiting." -ForegroundColor Red
                exit 1
            }
            
            Write-Host "Retrying in `$SleepInterval seconds..." -ForegroundColor Yellow
            Start-Sleep -Seconds `$SleepInterval
        }
    }
}
catch {
    Write-Host "Service wrapper error: `$_" -ForegroundColor Red
    exit 1
}
"@
    
    Set-Content -Path $WrapperScript -Value $WrapperContent
    Write-Host "Created service wrapper: $WrapperScript" -ForegroundColor Green
    
    # Install service using NSSM (Non-Sucking Service Manager) if available
    # Otherwise use sc.exe
    $NSSMPath = "nssm.exe"
    if (Get-Command $NSSMPath -ErrorAction SilentlyContinue) {
        Write-Host "Using NSSM to install service..." -ForegroundColor Cyan
        
        & $NSSMPath install $ServiceName `
            "powershell.exe" `
            "-NoProfile -ExecutionPolicy Bypass -File `"$WrapperScript`""
        
        & $NSSMPath set $ServiceName DisplayName $DisplayName
        & $NSSMPath set $ServiceName Description $Description
        & $NSSMPath set $ServiceName AppDirectory $ProjectRoot
        & $NSSMPath set $ServiceName AppNoConsole 1
        
        # Set restart behavior
        & $NSSMPath set $ServiceName AppExit Default Restart
        & $NSSMPath set $ServiceName AppRestartDelay 5000
        
        Write-Host "Service installed with NSSM" -ForegroundColor Green
    }
    else {
        Write-Host "NSSM not found. Using sc.exe (limited functionality)" -ForegroundColor Yellow
        Write-Host "For better service management, install NSSM:" -ForegroundColor Yellow
        Write-Host "  https://nssm.cc/download" -ForegroundColor Yellow
        
        # Create service batch file
        $BatchPath = Join-Path $ProjectRoot "service_start.bat"
        $BatchContent = @"
@echo off
REM Trading Bot Service Startup Script
cd /d "$ProjectRoot"
call "$VenvPath\Scripts\activate.bat"
python example_runner.py --symbols EURUSD GBPUSD USDJPY AUDUSD EURJPY --demo
"@
        Set-Content -Path $BatchPath -Value $BatchContent
        
        # Register service
        sc.exe create $ServiceName `
            binPath= "$PythonPath `"$BatchPath`"" `
            DisplayName= "$DisplayName" `
            start= auto `
            obj= "LocalSystem"
        
        # Set description
        sc.exe description $ServiceName "$Description"
        
        Write-Host "Service installed with sc.exe" -ForegroundColor Green
    }
    
    Write-Host "✓ Service installation complete" -ForegroundColor Green
    Write-Host "Note: Start the service manually or use:" -ForegroundColor Yellow
    Write-Host "  Start-Service -Name $ServiceName" -ForegroundColor Yellow
}

# Function to remove service
function Remove-TradingBotService {
    Write-Host "Removing Trading Bot service..." -ForegroundColor Cyan
    
    # Stop service if running
    if (Test-ServiceExists $ServiceName) {
        Write-Host "Stopping service..." -ForegroundColor Yellow
        Stop-Service -Name $ServiceName -ErrorAction SilentlyContinue -Force
        Start-Sleep -Seconds 2
    }
    
    $NSSMPath = "nssm.exe"
    if (Get-Command $NSSMPath -ErrorAction SilentlyContinue) {
        & $NSSMPath remove $ServiceName confirm
        Write-Host "Service removed with NSSM" -ForegroundColor Green
    }
    else {
        sc.exe delete $ServiceName
        Write-Host "Service removed with sc.exe" -ForegroundColor Green
    }
    
    Write-Host "✓ Service removal complete" -ForegroundColor Green
}

# Function to start service
function Start-TradingBotService {
    Write-Host "Starting Trading Bot service..." -ForegroundColor Cyan
    
    if (-not (Test-ServiceExists $ServiceName)) {
        Write-Host "Service not installed. Run with -Install first." -ForegroundColor Red
        return
    }
    
    Start-Service -Name $ServiceName
    Write-Host "✓ Service started" -ForegroundColor Green
}

# Function to stop service
function Stop-TradingBotService {
    Write-Host "Stopping Trading Bot service..." -ForegroundColor Cyan
    
    if (-not (Test-ServiceExists $ServiceName)) {
        Write-Host "Service not installed." -ForegroundColor Red
        return
    }
    
    Stop-Service -Name $ServiceName -Force
    Write-Host "✓ Service stopped" -ForegroundColor Green
}

# Function to show service status
function Show-TradingBotStatus {
    Write-Host "Trading Bot Service Status" -ForegroundColor Cyan
    Write-Host "=============================" -ForegroundColor Cyan
    
    if (Test-ServiceExists $ServiceName) {
        $Service = Get-Service -Name $ServiceName
        Write-Host "Service Name: $($Service.Name)" -ForegroundColor White
        Write-Host "Display Name: $($Service.DisplayName)" -ForegroundColor White
        Write-Host "Status: $($Service.Status)" -ForegroundColor $(
            if ($Service.Status -eq "Running") { "Green" } else { "Yellow" }
        )
        Write-Host "Startup Type: $($Service.StartType)" -ForegroundColor White
        
        # Try to get recent logs if running with NSSM
        $LogFile = Join-Path $ProjectRoot "service_logs\$ServiceName.log"
        if (Test-Path $LogFile) {
            Write-Host "`nRecent Logs (last 10 lines):" -ForegroundColor Cyan
            Get-Content -Path $LogFile -Tail 10 | Write-Host
        }
    }
    else {
        Write-Host "Service not installed" -ForegroundColor Yellow
    }
}

# Main script logic
if ($Uninstall) {
    Remove-TradingBotService
}
elseif ($Stop) {
    Stop-TradingBotService
}
elseif ($Start) {
    Start-TradingBotService
}
elseif ($Status) {
    Show-TradingBotStatus
}
else {
    # Default: Install
    Install-TradingBotService
    Write-Host ""
    Write-Host "Installation Summary:" -ForegroundColor Cyan
    Write-Host "=====================" -ForegroundColor Cyan
    Write-Host "Service Name: $ServiceName" -ForegroundColor White
    Write-Host "Display Name: $DisplayName" -ForegroundColor White
    Write-Host "Project Root: $ProjectRoot" -ForegroundColor White
    Write-Host "Python: $PythonPath" -ForegroundColor White
    Write-Host ""
    Write-Host "Common Commands:" -ForegroundColor Yellow
    Write-Host "  Start service:   powershell -File install_windows_service.ps1 -Start" -ForegroundColor White
    Write-Host "  Stop service:    powershell -File install_windows_service.ps1 -Stop" -ForegroundColor White
    Write-Host "  Service status:  powershell -File install_windows_service.ps1 -Status" -ForegroundColor White
    Write-Host "  Uninstall:       powershell -File install_windows_service.ps1 -Uninstall" -ForegroundColor White
    Write-Host ""
    Write-Host "Or use Windows Services Manager:" -ForegroundColor Yellow
    Write-Host "  services.msc" -ForegroundColor White
}

exit 0
