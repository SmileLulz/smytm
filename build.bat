@echo off
rem (UNTESTED SCRIPT)
setlocal enabledelayedexpansion

set "VERSION=dev"
if exist VERSION (
    for /f "usebackq delims=" %%v in ("VERSION") do (
        set "VERSION=%%v"
        goto :version_done
    )
)
:version_done

if "%~1"=="" goto :usage
if /i "%~1"=="-h" goto :usage
if /i "%~1"=="--help" goto :usage
if /i "%~1"=="go" goto :run_go
if /i "%~1"=="cross" goto :run_cross
if /i "%~1"=="arch" goto :run_pkg
if /i "%~1"=="deb" goto :run_pkg
if /i "%~1"=="rpm" goto :run_pkg

echo Error: unknown command "%~1" 1>&2
goto :usage

:run_go
set CGO_ENABLED=0
echo Building for windows/amd64 -^> smytm.exe ...
go build -trimpath -buildvcs=false -ldflags "-s -w -X main.version=!VERSION!" -o smytm.exe ./src %*
exit /b %ERRORLEVEL%

:run_cross
set "OUTDIR=dist"
if not "%~2"=="" set "OUTDIR=%~2"
if not exist "!OUTDIR!" mkdir "!OUTDIR!"

call :build_target !OUTDIR! linux amd64      || exit /b 1
call :build_target !OUTDIR! linux arm64      || exit /b 1
call :build_target !OUTDIR! linux riscv64    || exit /b 1
call :build_target !OUTDIR! darwin amd64     || exit /b 1
call :build_target !OUTDIR! darwin arm64     || exit /b 1
call :build_target !OUTDIR! windows amd64    || exit /b 1
call :build_target !OUTDIR! windows arm64    || exit /b 1
call :build_target !OUTDIR! android arm64    || exit /b 1

exit /b 0

:run_pkg
echo Error: Package building (arch, deb, rpm) is only supported on Linux. 1>&2
echo Please run this command inside WSL or a native Linux environment.
exit /b 1

:build_target
set "BT_OUTDIR=%~1"
set "BT_OS=%~2"
set "BT_ARCH=%~3"
set "BT_EXT="
if "!BT_OS!"=="windows" set "BT_EXT=.exe"

set "BT_OUT=!BT_OUTDIR!\smytm-!VERSION!-!BT_OS!-!BT_ARCH!!BT_EXT!"
echo Building !BT_OS!/!BT_ARCH! -^> !BT_OUT! ...

set CGO_ENABLED=0
set GOOS=!BT_OS!
set GOARCH=!BT_ARCH!

go build -trimpath -buildvcs=false -ldflags "-s -w -X main.version=!VERSION!" -o "!BT_OUT!" ./src
exit /b %ERRORLEVEL%

:usage
echo Usage: %~nx0 ^<command^>
echo.
echo Commands:
echo   go             Build for the current OS/arch (outputs .\smytm.exe)
echo   cross          Cross-compile all supported OS/arch targets into .\dist
echo.
echo Note: The 'arch', 'deb', and 'rpm' commands are Linux-only.
exit /b 1
