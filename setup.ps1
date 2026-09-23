[CmdletBinding()]
param(
    [string]$PythonExe,
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$venvRoot = Join-Path $projectRoot '.venv'
$venvPython = Join-Path $venvRoot 'Scripts\python.exe'
$requirements = Join-Path $projectRoot 'requirements-lock.txt'

function Invoke-PythonChecked {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Python command failed (exit $LASTEXITCODE): $($Arguments -join ' ')" }
}
function Assert-CompatiblePython {
    param([string]$Executable)
    Invoke-PythonChecked -Executable $Executable -Arguments @('-c', 'import struct,sys; print(sys.version); assert sys.version_info[:2] == (3,12), "Python 3.12 is required"; assert struct.calcsize("P") == 8, "64-bit Python is required"')
}

try {
    if ($env:OS -ne 'Windows_NT') { throw 'This setup script supports Windows only.' }
    if (-not (Test-Path -LiteralPath $requirements)) { throw 'requirements-lock.txt is missing. Download or clone the complete repository.' }
    if (-not (Test-Path -LiteralPath $venvPython)) {
        if ($CheckOnly) { throw 'No .venv found. Run Setup.cmd first.' }
        if (Test-Path -LiteralPath $venvRoot) { throw 'An incomplete .venv exists. Rename it before retrying; setup will not delete it.' }
        if (-not $PythonExe) {
            $launcher = Get-Command py.exe -ErrorAction SilentlyContinue
            if ($launcher) {
                $candidate = & $launcher.Source -3.12 -c 'import sys; print(sys.executable)' 2>$null
                if ($LASTEXITCODE -eq 0) { $PythonExe = ($candidate | Select-Object -Last 1) }
            }
            if (-not $PythonExe) {
                $pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
                if ($pythonCommand -and $pythonCommand.Source -notlike '*\WindowsApps\*') { $PythonExe = $pythonCommand.Source }
            }
        }
        if (-not $PythonExe) { throw 'Install 64-bit Python 3.12 from https://www.python.org/downloads/windows/ (include the Python launcher), then rerun Setup.cmd. Or run .\setup.ps1 -PythonExe "C:\path\to\python.exe".' }
        Assert-CompatiblePython -Executable $PythonExe
        Write-Host 'Creating the project Python environment...'
        Invoke-PythonChecked -Executable $PythonExe -Arguments @('-m', 'venv', $venvRoot)
    }
    Assert-CompatiblePython -Executable $venvPython
    if (-not $CheckOnly) {
        Write-Host 'Installing the pinned dependencies. Downloads may take several minutes...'
        Invoke-PythonChecked -Executable $venvPython -Arguments @('-m', 'pip', 'install', '--requirement', $requirements)
    }
    Invoke-PythonChecked -Executable $venvPython -Arguments @('-m', 'pip', 'check')
    $libraryBin = Join-Path $venvRoot 'Library\bin'
    $mathDll = Join-Path $libraryBin 'mkl_rt.2.dll'
    if (-not (Test-Path -LiteralPath $mathDll)) { throw "MKL runtime missing: $mathDll. Rerun Setup.cmd to install the locked MKL package." }
    # Changes apply only to this setup process and child processes.
    $env:PATH = "$libraryBin;$(Join-Path $venvRoot 'Scripts');$env:PATH"
    $env:DEVSIM_MATH_LIBS = $mathDll
    $env:OMP_NUM_THREADS = '2'
    $env:MKL_NUM_THREADS = '2'
    Invoke-PythonChecked -Executable $venvPython -Arguments @((Join-Path $projectRoot 'check_setup.py'))
    $pv = Get-Command paraview.exe -ErrorAction SilentlyContinue
    $pvPath = if ($pv) { $pv.Source } else { $null }
    if (-not $pvPath -and $env:ProgramFiles) {
        $pvPath = Get-ChildItem -Path (Join-Path $env:ProgramFiles 'ParaView*\bin\paraview.exe') -File -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
    }
    if ($pvPath) { Write-Host "ParaView found: $pvPath" }
    else { Write-Host 'ParaView is optional and installed separately: https://www.paraview.org/download/' }
    Write-Host ''
    Write-Host 'PASS: IH2662 simulation environment is ready.' -ForegroundColor Green
    Write-Host 'Next: open week4\START-HERE.md or double-click week4\Run-Week4.cmd.'
    exit 0
} catch {
    Write-Host ''
    Write-Host ('SETUP FAILED: ' + $_.Exception.Message) -ForegroundColor Red
    Write-Host 'Fix the reported issue and rerun Setup.cmd. Existing simulation results are preserved.'
    exit 1
}
