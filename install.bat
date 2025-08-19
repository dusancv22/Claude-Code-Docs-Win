@echo off
REM Claude Code Docs Installer for Windows
REM This batch file runs the Python installer

echo Claude Code Docs - Windows Installer
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Run the Python installer
python "%~dp0install.py" %*

REM Check if installation was successful
if %errorlevel% neq 0 (
    echo.
    echo Installation failed. Please check the error messages above.
    pause
    exit /b %errorlevel%
)

echo.
echo Installation complete!
pause