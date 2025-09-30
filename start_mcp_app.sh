#!/bin/bash
# Enhanced Healthcare Payor AI System - MCP Version Startup Script
echo "🚀 Starting Enhanced Healthcare Payor AI System (MCP Version)..."
echo "=================================================================="
echo "🔧 Activating conda environment: azure_databricks_py311"
source ~/anaconda3/etc/profile.d/conda.sh
conda activate azure_databricks_py311

echo "🔧 Setting Databricks profile: DEFAULT_azure"
export DATABRICKS_PROFILE="DEFAULT_azure"

# Check if MCP dependencies are installed
echo "🔍 Checking MCP dependencies..."
python -c "import databricks_mcp; print('✅ databricks-mcp installed')" || {
    echo "❌ databricks-mcp not found. Installing MCP dependencies..."
    pip install -r requirements-mcp.txt
}

# Find available port
PORT=8503
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port $PORT is in use, trying port 8504..."
    PORT=8504
fi

echo "🌐 Starting Streamlit MCP app on port $PORT"
echo "📍 Local URL: http://localhost:$PORT"
echo "📍 Network URL: http://10.248.121.198:$PORT"
echo ""
echo "🔧 MCP Servers:"
echo "   - Genie: https://adb-984752964297111.11.azuredatabricks.net/api/2.0/mcp/genie/01f06a3068a81406a386e8eaefc74545"
echo "   - UC Functions: https://adb-984752964297111.11.azuredatabricks.net/api/2.0/mcp/functions/my_catalog/payer_silver"
echo ""

streamlit run enhanced_healthcare_payor_app_mcp.py \
    --server.port $PORT \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --browser.gatherUsageStats false

echo ""
echo "✅ Streamlit MCP app stopped"
