@echo off
echo ====================================
echo   Offline Vector Database Refresh Tool
echo ====================================
echo.

REM Switch to backend directory
cd /d "%~dp0backend"

REM Check if confluence_export.json file exists
if not exist "..\data\confluence_export.json" (
    echo Error: confluence_export.json file not found in data directory!
    echo Please ensure this file exists before running this script.
    echo.
    pause
    exit /b 1
)

echo Importing data from confluence_export.json to vector database...
echo.

REM Run data importer to refresh vector database
python data_importer.py import

REM Check if import was successful
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ====================================
    echo   ✓ Vector database refresh completed successfully!
    echo   Vector database has been updated with latest data.
    echo ====================================
) else (
    echo.
    echo ====================================
    echo   ✗ Error occurred during vector database refresh!
    echo   Please check the error messages above.
    echo ====================================
)

echo.
echo Press any key to exit...
pause >nul