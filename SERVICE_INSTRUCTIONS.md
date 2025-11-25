# Confluence Finder Service Instructions

## Starting the Services

To start both the backend and frontend services:

1. Double-click on `start.bat` in the root directory
2. The script will automatically:
   - Launch the backend Flask server
   - Launch the frontend development server
   - Show you the URLs where the services are running

## Stopping the Services

To stop all services:

1. Double-click on `stop.bat` in the root directory
2. The script will automatically terminate all related processes

## Service Information

- **Backend Service**: Runs on http://localhost:5000
- **Frontend Service**: Runs on http://localhost:3000

## Notes

- Make sure you have all dependencies installed before starting the services:
  - For backend: Run `pip install -r backend/requirements.txt`
  - For frontend: Run `npm install` in the frontend directory
- The services will run in separate command windows
- Press any key in the main window to close it after starting services
