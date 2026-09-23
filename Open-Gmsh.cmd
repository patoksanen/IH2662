@echo off
cd /d "%~dp0"
call ih2662.cmd week1.py gmsh
if errorlevel 1 pause
