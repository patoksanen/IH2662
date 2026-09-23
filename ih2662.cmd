@echo off
setlocal
if not exist "%~dp0.venv\Scripts\python.exe" (
 echo Python environment missing. Run Setup.cmd in the IH2662 folder first.
 exit /b 1
)
set "PATH=%~dp0.venv\Library\bin;%~dp0.venv\Scripts;%PATH%"
set "DEVSIM_MATH_LIBS=%~dp0.venv\Library\bin\mkl_rt.2.dll"
set "OMP_NUM_THREADS=2"
set "MKL_NUM_THREADS=2"
"%~dp0.venv\Scripts\python.exe" %*
