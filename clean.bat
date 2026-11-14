@echo off
rem (UNTESTED SCRIPT)
rem Removes build artifacts produced by build.bat and build.sh
setlocal

echo Removing build artifacts...

if exist smytm.exe del /f /q smytm.exe
if exist smytm del /f /q smytm
if exist dist rd /s /q dist
if exist packaging\arch\src rd /s /q packaging\arch\src
if exist packaging\arch\pkg rd /s /q packaging\arch\pkg
if exist packaging\arch\*.pkg.tar.zst del /f /q packaging\arch\*.pkg.tar.zst
if exist packaging\arch\*.src.tar.* del /f /q packaging\arch\*.src.tar.*

echo Done
endlocal
