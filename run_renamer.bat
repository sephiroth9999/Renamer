@echo off
echo Starting Renamer...
python renamer.py
if errorlevel 1 (
    echo.
    echo Error: Python not found or script failed to run.
    echo Please make sure Python 3 is installed.
    pause
)
