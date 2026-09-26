@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" goto menu
call "%~dp0..\ih2662.cmd" "%~dp0field_plate\field_plate.py" %*
exit /b %errorlevel%
:menu
echo IH2662 - Silicon field plate over oxide
echo 1. Generate structure and mesh
echo 2. View mesh in Gmsh
echo 3. Check mesh import and equation setup
echo 4. Run full reverse-bias sweep
echo 5. Run separate 1 V diagnostic test
set /p choice=Choose 1-5:
if "%choice%"=="1" call "%~dp0..\ih2662.cmd" "%~dp0field_plate\field_plate.py" mesh
if "%choice%"=="2" call "%~dp0..\ih2662.cmd" "%~dp0field_plate\field_plate.py" view-mesh
if "%choice%"=="3" call "%~dp0..\ih2662.cmd" "%~dp0field_plate\field_plate.py" check
if "%choice%"=="4" call "%~dp0..\ih2662.cmd" "%~dp0field_plate\field_plate.py" run
if "%choice%"=="5" call "%~dp0..\ih2662.cmd" "%~dp0field_plate\field_plate.py" smoke
pause
