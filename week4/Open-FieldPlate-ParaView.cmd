@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0field_plate\open_paraview.ps1" %*
if errorlevel 1 pause
