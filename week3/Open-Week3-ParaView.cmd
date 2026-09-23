@echo off
cd /d "%~dp0"
if not exist "results\baseline_double_h1\final.vtu" (
echo Run the Week 3 reverse-bias sweep first.
pause
exit /b 1
)
start "" "C:\Program Files\ParaView 6.1.1\bin\paraview.exe" "--data=%~dp0results\baseline_double_h1\final.vtu"
