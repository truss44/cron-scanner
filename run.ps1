<#
.SYNOPSIS
    Windows runner for Cron Scanner. Creates a virtual environment if possible, installs requirements, and runs the scanner.

.EXAMPLES
    # Install dependencies (venv if available, else user site) and exit
    ./run.ps1 -Install

    # Run using the current user's crontab for the next 24 hours (default)
    ./run.ps1

    # Run with explicit options
    ./run.ps1 -File sample_crontab.txt -TimeSpan 2d -Format csv
    ./run.ps1 -StartTime 2025-01-01 -EndTime 2025-01-07 -Format json -Output output.json

.NOTES
    - This script does not require manual activation of the virtual environment.
    - If a venv cannot be created, it falls back to user-level pip installation and adjusts PYTHONPATH.
#>

[CmdletBinding()]
param(
    [switch]$Install,
    [switch]$Run,
    [switch]$Uninstall,
    [string]$File,
    [string]$StartTime,
    [string]$EndTime,
    [string]$TimeSpan,
    [ValidateSet('csv','json','xlsx','text','pdf')]
    [string]$Format = 'csv',
    [string]$Output
)

$ErrorActionPreference = 'Stop'

# Determine project directory (directory of this script)
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $ProjectDir 'venv'
$VenvPython = Join-Path $VenvDir 'Scripts/python.exe'

function Test-Command($name) {
    try { Get-Command $name -ErrorAction Stop | Out-Null; return $true } catch { return $false }
}

# Choose Python invoker (prefer python, then py -3)
$UsePyLauncher = $false
if (Test-Command 'python') {
    $PyCmd = 'python'
    $PyArgs = @()
} elseif (Test-Command 'py') {
    $PyCmd = 'py'
    $PyArgs = @('-3')
    $UsePyLauncher = $true
} else {
    Write-Error 'Python 3 was not found on PATH. Please install Python 3 and try again.'
}

function Invoke-Py([string[]]$Args) {
    if ($UsePyLauncher) {
        & py @('-3') @Args
    } else {
        & python @Args
    }
}

# Ensure we operate from the project directory
Set-Location $ProjectDir

$UseVenv = $true

function Setup-Venv {
    param([string]$Dir)
    if (-not (Test-Path $Dir)) {
        Write-Host 'Creating virtual environment...' -ForegroundColor Cyan
        try {
            Invoke-Py @('-m','venv', $Dir)
        } catch {
            Write-Warning 'Could not create a virtual environment (python venv module may be missing). Falling back to user-level installs.'
            $script:UseVenv = $false
        }
    }

    if ($script:UseVenv -and -not (Test-Path $VenvPython)) {
        Write-Warning 'Virtual environment appears incomplete. Falling back to user-level installs.'
        $script:UseVenv = $false
    }
}

function Ensure-Pip {
    if ($script:UseVenv) {
        & $VenvPython -m pip --version | Out-Null
    } else {
        try {
            Invoke-Py @('-m','pip','--version') | Out-Null
        } catch {
            Write-Host 'Bootstrapping pip with ensurepip...' -ForegroundColor Cyan
            try {
                Invoke-Py @('-m','ensurepip','--upgrade') | Out-Null
            } catch {
                Write-Error 'Failed to bootstrap pip automatically. Please install pip (e.g., "py -m ensurepip --upgrade") and re-run.'
            }
        }
    }
}

function Install-Requirements {
    if ($script:UseVenv) {
        Write-Host 'Installing requirements into virtual environment...' -ForegroundColor Cyan
        & $VenvPython -m pip install -r (Join-Path $ProjectDir 'requirements.txt')
    } else {
        Write-Host 'Installing requirements into user site-packages...' -ForegroundColor Cyan
        Invoke-Py @('-m','pip','install','--user','-r', (Join-Path $ProjectDir 'requirements.txt'))
        # Ensure user site is discoverable at runtime
        $userSite = (Invoke-Py @('-c','import site; print(site.getusersitepackages())') | Select-Object -First 1).Trim()
        if ($userSite) {
            $env:PYTHONPATH = if ($env:PYTHONPATH) { "$userSite;$($env:PYTHONPATH)" } else { $userSite }
        }
    }
}

function Run-Scanner {
    # Build argument list for the Python module
    $argsList = @()
    if ($File)      { $argsList += @('--file', $File) }
    if ($StartTime) { $argsList += @('--start-time', $StartTime) }
    if ($EndTime)   { $argsList += @('--end-time', $EndTime) }
    if ($TimeSpan)  { $argsList += @('--time-span', $TimeSpan) }
    if ($Format)    { $argsList += @('--format', $Format) }
    if ($Output)    { $argsList += @('--output', $Output) }

    if ($script:UseVenv) {
        & $VenvPython -m cron_scanner.scanner @argsList
    } else {
        Invoke-Py @('-m','cron_scanner.scanner') @argsList
    }
}

function Cleanup-Venv {
    if (Test-Path $VenvDir) {
        Write-Host 'Removing virtual environment...' -ForegroundColor Yellow
        Remove-Item -Recurse -Force $VenvDir
        Write-Host 'Virtual environment removed.' -ForegroundColor Green
    } else {
        Write-Host 'Virtual environment not found. Nothing to remove.' -ForegroundColor Yellow
    }
}

# Default behavior: run if no mode switches provided
if (-not $Install -and -not $Run -and -not $Uninstall) {
    $Run = $true
}

if ($Install) {
    Setup-Venv -Dir $VenvDir
    Ensure-Pip
    Install-Requirements
    Write-Host "Installation complete. Run './run.ps1' to start the cron scanner." -ForegroundColor Green
    exit 0
}

if ($Uninstall) {
    Cleanup-Venv
    exit 0
}

if ($Run) {
    Setup-Venv -Dir $VenvDir
    Ensure-Pip
    Install-Requirements
    Run-Scanner
}
