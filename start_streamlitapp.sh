#!/bin/bash

# Enhanced Healthcare Payor AI System - Streamlit App Startup Script
# This script starts the Streamlit app with all correct parameters

echo "🚀 Starting Enhanced Healthcare Payor AI System..."
echo "=================================================="

# Set the working directory
cd /Users/vik.malhotra/hospital_ai_system/payor-billing-customer-care

# Activate the conda environment
echo "🔧 Activating conda environment: azure_databricks_py311"
source ~/anaconda3/etc/profile.d/conda.sh
conda activate azure_databricks_py311

# Set Databricks profile
echo "🔧 Setting Databricks profile: DEFAULT_azure"
export DATABRICKS_PROFILE="DEFAULT_azure"

# Check if port 8502 is available, if not try 8503
PORT=8502
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port $PORT is in use, trying port 8503..."
    PORT=8503
fi

echo "🌐 Starting Streamlit app on port $PORT"
echo "📍 Local URL: http://localhost:$PORT"
echo "📍 Network URL: http://10.248.121.198:$PORT"
echo ""

# Start the Streamlit app
streamlit run enhanced_healthcare_payor_app.py \
    --server.port $PORT \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --browser.gatherUsageStats false

echo ""
echo "✅ Streamlit app stopped"
