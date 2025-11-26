#!/bin/bash

# Confluence Finder - Environment Configuration Script
# Purpose: Configure environment variables for the project, including Kimi API Key

echo "==================================="
echo "Confluence Finder Environment Configuration Script"
echo "==================================="

# Ensure we're in the correct directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check backend directory
if [ ! -d "backend" ]; then
    echo "Error: backend directory not found"
    exit 1
fi

# Copy example environment variable file
if [ ! -f "backend/.env" ]; then
    if [ -f "backend/.env.example" ]; then
        echo "Creating .env file from .env.example..."
        cp backend/.env.example backend/.env
        echo ".env file created"
    else
        echo "Warning: .env.example file not found. Creating new .env file..."
        touch backend/.env
        # Add basic configuration
        cat > backend/.env << EOF
# LLM API configuration (for Q&A only)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-3.5-turbo

# Optional: Support other LLMs
LLM_TYPE=openai
# LLM_TYPE=claude
# LLM_TYPE=kimi

# Kimi LLM configuration
KIMI_API_KEY=
KIMI_API_BASE=https://api.moonshot.cn/v1
KIMI_MODEL=moonshot-v1-8k

# Local storage configuration
CHROMA_DB_PATH=./chroma_db

# Confluence API configuration (for data import only)
CONFLUENCE_URL=
CONFLUENCE_USERNAME=
CONFLUENCE_API_TOKEN=

# Application configuration
FLASK_ENV=production
FLASK_PORT=5000
EOF
        echo "Created new .env file with default configuration"
    fi
fi

echo "Current .env file configuration:"
echo "-----------------------------------"
grep -v '^#' backend/.env | grep -v '^$'
echo "-----------------------------------"

# Ask if user wants to set Kimi API Key
read -p "Would you like to set Kimi API Key? (y/n): " SET_KIMI
if [ "$SET_KIMI" = "y" ] || [ "$SET_KIMI" = "Y" ]; then
    read -p "Please enter Kimi API Key: " KIMI_KEY
    
    # Replace or add Kimi API Key
    if grep -q "KIMI_API_KEY=" backend/.env; then
        sed -i "s/KIMI_API_KEY=.*/KIMI_API_KEY=$KIMI_KEY/" backend/.env
    else
        echo "KIMI_API_KEY=$KIMI_KEY" >> backend/.env
    fi
    
    # Set LLM type to kimi
    if grep -q "LLM_TYPE=" backend/.env; then
        sed -i "s/^LLM_TYPE=.*/LLM_TYPE=kimi/" backend/.env
    else
        echo "LLM_TYPE=kimi" >> backend/.env
    fi
    
    echo "✅ Kimi API Key has been set!"
fi

# Ask if user wants to configure other environment variables
read -p "Would you like to configure other environment variables? (y/n): " SET_OTHER
if [ "$SET_OTHER" = "y" ] || [ "$SET_OTHER" = "Y" ]; then
    echo "==================================="
    echo "Configurable Environment Variables:"
    echo "1. OPENAI_API_KEY"
    echo "2. CONFLUENCE_URL"
    echo "3. CONFLUENCE_USERNAME"
    echo "4. CONFLUENCE_API_TOKEN"
    echo "5. FLASK_PORT"
    echo "6. Exit configuration"
    echo "==================================="
    
    while true; do
        read -p "Please select the environment variable to configure (1-6): " OPTION
        
        case $OPTION in
            1)
                read -p "Please enter OPENAI_API_KEY: " OPENAI_KEY
                sed -i "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=$OPENAI_KEY/" backend/.env
                echo "✅ OPENAI_API_KEY has been set!"
                ;;
            2)
                read -p "Please enter CONFLUENCE_URL: " CONFLUENCE_URL
                sed -i "s/CONFLUENCE_URL=.*/CONFLUENCE_URL=$CONFLUENCE_URL/" backend/.env
                echo "✅ CONFLUENCE_URL has been set!"
                ;;
            3)
                read -p "Please enter CONFLUENCE_USERNAME: " CONFLUENCE_USERNAME
                sed -i "s/CONFLUENCE_USERNAME=.*/CONFLUENCE_USERNAME=$CONFLUENCE_USERNAME/" backend/.env
                echo "✅ CONFLUENCE_USERNAME has been set!"
                ;;
            4)
                read -p "Please enter CONFLUENCE_API_TOKEN: " CONFLUENCE_API_TOKEN
                sed -i "s/CONFLUENCE_API_TOKEN=.*/CONFLUENCE_API_TOKEN=$CONFLUENCE_API_TOKEN/" backend/.env
                echo "✅ CONFLUENCE_API_TOKEN has been set!"
                ;;
            5)
                read -p "Please enter FLASK_PORT (default 5000): " FLASK_PORT
                if [ -z "$FLASK_PORT" ]; then
                    FLASK_PORT=5000
                fi
                sed -i "s/FLASK_PORT=.*/FLASK_PORT=$FLASK_PORT/" backend/.env
                echo "✅ FLASK_PORT has been set to $FLASK_PORT!"
                ;;
            6)
                echo "Exiting configuration..."
                break
                ;;
            *)
                echo "Invalid option, please try again"
                ;;
        esac
    done
fi

echo "==================================="
echo "Environment configuration completed!"
echo "==================================="
echo "Important Notes:"
echo "1. Kimi API Key is stored in backend/.env file"
echo "2. Do not commit the .env file containing API keys to version control"
echo "3. In production environments, it is recommended to use environment variables or key management services"
echo "==================================="