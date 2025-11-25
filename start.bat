@echo off

echo Starting Confluence Finder services...

REM Start backend service
cd backend
start "Backend Server" cmd /k "python app.py"
cd ..

REM Wait for backend to start
ping 127.0.0.1 -n 3 > nul

REM Start frontend service
cd frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo Services started successfully!
echo Backend service running at http://localhost:5000
echo Frontend service running at http://localhost:3000
echo Press any key to exit this window...
pause > nul