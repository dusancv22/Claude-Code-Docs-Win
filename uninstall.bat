@echo off
REM Claude Code Docs Uninstaller for Windows
REM This batch file runs the Python uninstaller

echo Claude Code Docs - Windows Uninstaller
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo.
    echo Cannot run uninstaller without Python
    pause
    exit /b 1
)

REM Run the Python uninstaller
python "%~dp0uninstall.py" %*

REM Check if uninstallation was successful
if %errorlevel% neq 0 (
    echo.
    echo Uninstallation failed. Please check the error messages above.
    pause
    exit /b %errorlevel%
)

echo.
echo Uninstallation complete!
pause