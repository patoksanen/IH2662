@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" goto menu
call "%~dp0..\ih2662.cmd" "%~dp0guard_ring.py" %*
exit /b %errorlevel%
:menu
echo IH2662 Week 4 - Silicon floating guard ring
echo 1. Generate structure and mesh
echo 2. View mesh in Gmsh
echo 3. Check DEVSIM import and doping
echo 4. Run reverse-bias sweep (can take a long time)
set /p choice=Choose 1-4: 
if "%choice%"=="1" call "%~dp0..\ih2662.cmd" "%~dp0guard_ring.py" mesh
if "%choice%"=="2" call "%~dp0..\ih2662.cmd" "%~dp0guard_ring.py" view-mesh
if "%choice%"=="3" call "%~dp0..\ih2662.cmd" "%~dp0guard_ring.py" check
if "%choice%"=="4" call "%~dp0..\ih2662.cmd" "%~dp0guard_ring.py" run
pause
