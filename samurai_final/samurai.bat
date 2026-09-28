@echo off
REM SAMURAI v1.1 — Windows Launcher — xtobe-shadow
REM Smart Git Bypass integrated

setlocal

set "SAMURAI_DIR=%~dp0"
set "PYTHON=python"

if "%1"=="" (
    echo.
    echo SAMURAI v1.1 Build Machine
    echo ===========================
    echo.
    echo Usage:
    echo   samurai.bat init ^<project_name^>
    echo   samurai.bat run "commands" --n 9 --backend a1111
    echo   samurai.bat pipeline full --brief "..."
    echo   samurai.bat deploy --image hero.jpg
    echo   samurai.bat git [init-smart|commit-smart|push-smart|tag-smart|sync]
    echo.
    echo For full help: python samurai_cli.py --help
    echo.
    goto :eof
)

REM Smart Git Bypass handler
if "%1"=="git" (
  python "%SAMURAI_DIR%Code\samurai_git.py" %2 %3 %4 %5
  exit /b
)

%PYTHON% "%SAMURAI_DIR%Code\samurai_cli.py" %*

endlocal
