#!/bin/bash

# Healthcare Payor AI System Startup Script
# Flexible startup script with environment configuration

set -e

# Default values
CONDA_ENV="azure_databricks"
CATALOG="my_catalog"
SCHEMA="payer_silver"
LLM_ENDPOINT="databricks-meta-llama-3-3-70b-instruct"
PORT=8501
HOST="localhost"
DEBUG=false
TEST_CONNECTION=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --conda-env)
            CONDA_ENV="$2"
            shift 2
            ;;
        --catalog)
            CATALOG="$2"
            shift 2
            ;;
        --schema)
            SCHEMA="$2"
            shift 2
            ;;
        --llm-endpoint)
            LLM_ENDPOINT="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        --test-connection)
            TEST_CONNECTION=true
            shift
            ;;
        --help)
            echo "Healthcare Payor AI System Startup Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --conda-env ENV        Conda environment name (default: azure_databricks)"
            echo "  --catalog CATALOG       Unity Catalog name (default: my_catalog)"
            echo "  --schema SCHEMA         Schema name (default: payer_silver)"
            echo "  --llm-endpoint ENDPOINT LLM endpoint name (default: databricks-meta-llama-3-3-70b-instruct)"
            echo "  --port PORT            Streamlit port (default: 8501)"
            echo "  --host HOST            Streamlit host (default: localhost)"
            echo "  --debug                Enable debug mode"
            echo "  --test-connection      Test connections before starting"
            echo "  --help                 Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Use defaults"
            echo "  $0 --catalog my_catalog --schema payer_silver"
            echo "  $0 --llm-endpoint databricks-claude-3-5-sonnet"
            echo "  $0 --port 8502 --debug"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "🏥 Healthcare Payor AI System Startup Script"
echo "=============================================="

# Set environment variables
export HEALTHCARE_CATALOG="$CATALOG"
export HEALTHCARE_SCHEMA="$SCHEMA"
export HEALTHCARE_LLM_ENDPOINT="$LLM_ENDPOINT"
export HEALTHCARE_DEBUG="$DEBUG"

echo "📋 Configuration:"
echo "   - Conda Environment: $CONDA_ENV"
echo "   - Catalog: $CATALOG"
echo "   - Schema: $SCHEMA"
echo "   - LLM Endpoint: $LLM_ENDPOINT"
echo "   - Port: $PORT"
echo "   - Host: $HOST"
echo "   - Debug: $DEBUG"

# Test connections if requested
if [ "$TEST_CONNECTION" = true ]; then
    echo ""
    echo "🔍 Testing connections..."
    
    # Test conda environment
    if ! conda info --envs | grep -q "$CONDA_ENV"; then
        echo "❌ Conda environment '$CONDA_ENV' not found"
        exit 1
    fi
    echo "✅ Conda environment '$CONDA_ENV' found"
    
    # Test Databricks CLI
    if ! databricks workspace ls >/dev/null 2>&1; then
        echo "❌ Databricks CLI connection failed"
        echo "Please configure Databricks CLI with: databricks configure"
        exit 1
    fi
    echo "✅ Databricks CLI connection successful"
    
    # Test required packages
    if ! conda run -n "$CONDA_ENV" python -c "import databricks_langchain, unitycatalog_langchain, langchain" 2>/dev/null; then
        echo "❌ Required packages not available"
        echo "Installing packages in $CONDA_ENV..."
        conda run -n "$CONDA_ENV" pip install databricks-langchain unitycatalog-langchain[databricks] langchain langchain-core streamlit
        echo "✅ Packages installed successfully"
    else
        echo "✅ Required packages available"
    fi
    
    echo "✅ All connection tests passed"
fi

# Start the app
echo ""
echo "🚀 Starting Healthcare Payor AI System..."
echo "📱 App will be available at: http://$HOST:$PORT"

# Build the conda run command
CMD="conda run -n $CONDA_ENV streamlit run healthcare_payor_streamlit_app.py --server.port $PORT --server.address $HOST"

if [ "$DEBUG" = true ]; then
    CMD="$CMD --logger.level debug"
fi

echo "🔧 Running: $CMD"
echo ""

# Execute the command
exec $CMD