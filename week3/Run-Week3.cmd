@echo off
cd /d "%~dp0"
if not exist logs mkdir logs
if "%~1"=="" goto menu
call ..\ih2662.cmd silicon_baseline.py %*
exit /b %errorlevel%
:menu
echo IH2662 WEEK 3 - silicon junction
echo.
echo 1. Generate the baseline mesh
echo 2. Open the baseline mesh in Gmsh
echo 3. Solve at zero bias
echo 4. Run the reverse-bias sweep
echo 5. Run the flat-junction control
echo 6. Run a finer baseline mesh
echo 7. Open the guide
echo.
set /p choice=Choose 1-7: 
if "%choice%"=="1" call ..\ih2662.cmd silicon_baseline.py mesh > logs\mesh.log 2>&1
if "%choice%"=="2" call ..\ih2662.cmd silicon_baseline.py view-mesh
if "%choice%"=="3" call ..\ih2662.cmd silicon_baseline.py equilibrium > logs\equilibrium.log 2>&1
if "%choice%"=="4" call ..\ih2662.cmd silicon_baseline.py run > logs\baseline.log 2>&1
if "%choice%"=="5" call ..\ih2662.cmd silicon_baseline.py run --planar > logs\planar.log 2>&1
if "%choice%"=="6" call ..\ih2662.cmd silicon_baseline.py run --mesh-scale 0.7 > logs\fine.log 2>&1
if "%choice%"=="7" start "" notepad.exe "%~dp0START-HERE.txt"
echo.
if errorlevel 1 (echo FAILED: check the corresponding file in logs.) else (echo Finished. Check results and logs.)
pause
