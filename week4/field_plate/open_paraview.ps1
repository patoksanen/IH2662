param([string]$DataFile)
$ErrorActionPreference='Stop'
try {
    if (-not $DataFile) {
        $caseFolder=Join-Path $PSScriptRoot 'results\plate_L5_tox1_h0.025'
        $DataFile=Join-Path $caseFolder 'final.vtm'
        if (-not (Test-Path -LiteralPath $DataFile)) { $DataFile=Join-Path $caseFolder 'structure.vtm' }
    }
    if (-not (Test-Path -LiteralPath $DataFile)) { throw 'Generate the field-plate mesh first (Run-FieldPlate.cmd option 1).' }
    $exe=Get-Command paraview.exe -ErrorAction SilentlyContinue
    $pv=if ($exe) { $exe.Source } else { $null }
    if (-not $pv) { $pv=Get-ChildItem -Path (Join-Path $env:ProgramFiles 'ParaView*\bin\paraview.exe') -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName }
    if (-not $pv) { throw 'ParaView was not found. Install it or open the VTM file manually.' }
    # This launcher is explicitly opened by the user to view the interactive GUI.
    Start-Process -FilePath $pv -ArgumentList ('--data="'+(Resolve-Path -LiteralPath $DataFile).Path+'"')
} catch { Write-Host $_.Exception.Message; exit 1 }
