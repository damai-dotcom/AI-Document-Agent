@echo off

echo Stopping Confluence Finder services...

REM Terminate Python processes (backend service)
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Backend Server"

REM Terminate Node.js processes (frontend service)
taskkill /F /IM node.exe /FI "WINDOWTITLE eq Frontend Server"

echo Services stopped successfully!
echo Press any key to exit...
pause > nul