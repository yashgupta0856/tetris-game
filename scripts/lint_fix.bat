@echo off
REM Quick lint fix wrapper script for Windows

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

REM Change to project root
cd /d "%PROJECT_ROOT%"

REM Run the Python lint fix script
python scripts\lint_fix.py %*
