@echo off
title The Great Bag Buster - Polythene Bag Pop Game (Java Edition)
color 0A

echo ===================================================================
echo   THE GREAT BAG BUSTER! (Polythene Bag Burst Game)
echo   Java 2D Edition - High Performance 60 FPS
echo ===================================================================
echo.

:: Detect Java JDK
set JAVACMD="java"
if exist "C:\Program Files\Java\jdk-26.0.2.1\bin\java.exe" (
    set JAVACMD="C:\Program Files\Java\jdk-26.0.2.1\bin\java.exe"
)

echo Launching game...
%JAVACMD% BagBusterGame

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to run Java game.
    pause
)

