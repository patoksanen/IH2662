@echo off
cd /d "%~dp0"
call ih2662.cmd week1.py view
if errorlevel 1 pause
