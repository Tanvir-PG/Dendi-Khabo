@echo off
title The Great Bag Buster - Polythene Bag Pop Game
color 0B

echo ===================================================================
echo   THE GREAT BAG BUSTER! (Polythene Bag Burst Game)
echo   2D Animated Cartoon Game in Pygame
echo ===================================================================
echo.

:: Detect working Python
set PYTHON_CMD=

:: Check py launcher
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    goto :PYTHON_FOUND
)

:: Check python executable
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :PYTHON_FOUND
)

:PYTHON_NOT_FOUND
color 0C
echo [ERROR] Real Python is not installed on this computer!
echo.
echo The message "Python was not found..." is a default Windows shortcut.
echo.
echo -------------------------------------------------------------------
echo  HOW TO FIX IN 2 MINUTES:
echo -------------------------------------------------------------------
echo  1. Download Python from: https://www.python.org/downloads/
echo  2. Run the installer.
echo  3. IMPORTANT: Check the box at the bottom that says:
echo     "[X] Add python.exe to PATH"
echo  4. Click "Install Now".
echo  5. After installation completes, run this run_game.bat again!
echo -------------------------------------------------------------------
echo.
echo NOTE: Since you already have Java JDK installed on your PC, you can 
echo also double-click 'run_game_java.bat' to play this exact game immediately!
echo.
pause
exit /b 1

:PYTHON_FOUND
color 0B
echo [1/2] Found active Python: %PYTHON_CMD%
%PYTHON_CMD% --version

echo.
echo [2/2] Checking Pygame package...
%PYTHON_CMD% -c "import pygame" >nul 2>&1
if %errorlevel% neq 0 (
    echo Pygame is not installed yet. Installing Pygame now...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install Pygame via pip.
        pause
        exit /b 1
    )
)

echo.
echo ===================================================================
echo  Launching The Great Bag Buster Game! (900x600, 60 FPS)
echo  Controls:
echo    - HOLD [SPACEBAR]   : Blow air into the bag
echo    - RELEASE [SPACEBAR]: Stop blowing
echo    - PRESS [R]         : Restart
echo    - PRESS [M]         : Toggle Sound
echo ===================================================================
echo.

%PYTHON_CMD% main.py

if %errorlevel% neq 0 (
    echo.
    echo Game terminated with an error code: %errorlevel%
    pause
)

