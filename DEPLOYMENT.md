# Confluence Finder - Linux Deployment Guide

This document provides detailed steps for deploying Confluence Finder on a Linux EC2 instance.

## Prerequisites

Install the necessary software on your EC2 instance:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and Node.js
sudo apt install -y python3 python3-pip python3-venv nodejs npm

# Clone project code
git clone <your-repository-url> confluence_finder
cd confluence_finder
```

## Script Descriptions

The project contains the following main scripts:

### 1. setup_env.sh - Environment Configuration Script

**Purpose:** Configure environment variables required for the project, including Kimi API Key

**Usage:**

```bash
chmod +x setup_env.sh
./setup_env.sh
```

**Kimi API Key Setup:**

- After running this script, you will be prompted to set your Kimi API Key
- Kimi API Key will be stored in the `backend/.env` file
- The script will automatically set `LLM_TYPE` to `kimi`
- You can also configure other environment variables such as OpenAI API Key, Confluence connection information, etc.

### 2. import_data.sh - Data Import Script

**Purpose:** Import data from `data/confluence_export.json` file into the vector database

**Usage:**

```bash
chmod +x import_data.sh
./import_data.sh
```

**Features:**

- Automatically checks Python environment and dependencies
- Supports virtual environment or system Python
- Automatically executes `backend/data_importer.py` for data import
- Shows import time statistics

### 3. start_services.sh - Service Startup Script

**Purpose:** Start the backend Flask service and frontend development server

**Usage:**

```bash
chmod +x start_services.sh
./start_services.sh
```

**Features:**

- Automatically checks Python and Node.js environments
- Checks and configures environment variable files
- Starts backend and frontend services in the background
- Generates log files
- Shows service access addresses

## Deployment Steps

### 1. Configure Environment Variables

First, run the environment configuration script to set up Kimi API Key:

```bash
./setup_env.sh
```

Follow the prompts to enter your Kimi API Key. After completion, the script will set the following in the `backend/.env` file:

```
KIMI_API_KEY=your_kimi_api_key_here
LLM_TYPE=kimi
```

### 2. Import Data

If you need to import offline data, run the data import script:

```bash
./import_data.sh
```

This script will populate the vector database using data from the `data/confluence_export.json` file.

### 3. Start Services

Finally, start both backend and frontend services:

```bash
./start_services.sh
```

Once started, you can access the services at:

- Backend API: http://your-ec2-ip:5000
- Frontend Interface: http://your-ec2-ip:3000

## Important Notes

### Kimi API Key Configuration Location

The Kimi API Key is stored in the `backend/.env` file, configured with the following keys:

- `KIMI_API_KEY`: Your Kimi API key
- `LLM_TYPE`: Must be set to `kimi` to use the Kimi model
- `KIMI_API_BASE`: API base URL (default: https://api.moonshot.cn/v1)
- `KIMI_MODEL`: Kimi model to use (default: moonshot-v1-8k)

### Security Considerations

1. Do not commit the `.env` file containing API keys to version control
2. In production environments, consider using AWS Secrets Manager or other key management services
3. Ensure your EC2 instance's security group only allows necessary port access

### Troubleshooting

1. **Service Startup Failure**:

   - Check log files: `backend.log` and `frontend.log`
   - Ensure all dependencies are correctly installed

2. **Data Import Failure**:

   - Ensure the `data/confluence_export.json` file exists and has the correct format
   - Check if Python dependencies are fully installed

3. **Kimi API Connection Issues**:
   - Verify API key is correct
   - Check if network connection allows access to Kimi API

## Update and Maintenance

To update code and restart services:

```bash
# Pull latest code
git pull

# Stop existing services
kill <backend-pid> <frontend-pid>

# Restart services
./start_services.sh
```

## Extended Configuration

To customize ports or other configurations, edit the `backend/.env` file:

```bash
# Modify port
FLASK_PORT=8080

# Modify database path
CHROMA_DB_PATH=/path/to/chroma_db
```

You need to restart the services for configuration changes to take effect.
