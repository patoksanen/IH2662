@echo off
setlocal
set "PV=C:\Program Files\ParaView 6.1.1\bin\paraview.exe"
set "DATA=%~dp0results\guard_ring_gap3_h0.025\structure.vtu"
if not exist "%PV%" (
 echo Open ParaView manually and load the structure.vtu in the Week 4 results folder.
 pause
 exit /b 1
)
if not exist "%DATA%" (
 echo Run Run-Week4.cmd mesh first.
 pause
 exit /b 1
)
start "" "%PV%" "--data=%DATA%"
