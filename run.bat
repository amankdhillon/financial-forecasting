@echo off
REM Updated Windows batch script

echo ==============================================
echo   FUNDING ANALYSIS SUITE
echo ==============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Step 1: Installing dependencies...
pip install -r requirements.txt

echo.
echo Step 2: Running all analyses...
python main.py

echo.
echo ==============================================
echo   ALL ANALYSES COMPLETE!
echo ==============================================
echo.
echo Check the 'outputs' directory for results.
echo.
pause