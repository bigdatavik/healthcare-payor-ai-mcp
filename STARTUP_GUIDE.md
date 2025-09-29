# 🚀 Healthcare Payor AI System - Startup Guide

Flexible startup scripts for the Healthcare Payor AI System with configurable parameters.

## 📋 Quick Start

### **Option 1: Simple Shell Script (Recommended)**
```bash
# Use defaults
./start_app.sh

# Custom configuration
./start_app.sh --catalog my_catalog --schema payer_silver --port 8502
```

### **Option 2: Python Script (Advanced)**
```bash
# Use defaults
python start_healthcare_app.py

# Custom configuration
python start_healthcare_app.py --catalog my_catalog --schema payer_silver --llm-endpoint databricks-claude-3-5-sonnet
```

## 🔧 Configuration Options

### **Environment Configuration**
| Parameter | Environment Variable | Default | Description |
|-----------|---------------------|---------|-------------|
| `--conda-env` | `CONDA_ENV` | `azure_databricks` | Conda environment name |
| `--catalog` | `HEALTHCARE_CATALOG` | `my_catalog` | Unity Catalog name |
| `--schema` | `HEALTHCARE_SCHEMA` | `payer_silver` | Schema name |
| `--databricks-profile` | `HEALTHCARE_DATABRICKS_PROFILE` | `DEFAULT` | Databricks CLI profile |

### **LLM Configuration**
| Parameter | Environment Variable | Default | Description |
|-----------|---------------------|---------|-------------|
| `--llm-endpoint` | `HEALTHCARE_LLM_ENDPOINT` | `databricks-meta-llama-3-3-70b-instruct` | LLM endpoint name |
| `--llm-temperature` | `HEALTHCARE_LLM_TEMPERATURE` | `0.1` | LLM temperature (0.0-1.0) |

### **Streamlit Configuration**
| Parameter | Environment Variable | Default | Description |
|-----------|---------------------|---------|-------------|
| `--port` | `STREAMLIT_PORT` | `8501` | Streamlit port |
| `--host` | `STREAMLIT_HOST` | `localhost` | Streamlit host |

### **Debug Options**
| Parameter | Environment Variable | Default | Description |
|-----------|---------------------|---------|-------------|
| `--debug` | `HEALTHCARE_DEBUG` | `false` | Enable debug mode |
| `--test-connection` | - | `false` | Test connections before starting |

## 🎯 Usage Examples

### **Basic Usage**
```bash
# Start with defaults
./start_app.sh
```

### **Custom Catalog and Schema**
```bash
./start_app.sh --catalog my_healthcare_catalog --schema claims_data
```

### **Different LLM Endpoint**
```bash
./start_app.sh --llm-endpoint databricks-claude-3-5-sonnet
```

### **Custom Port and Debug Mode**
```bash
./start_app.sh --port 8502 --debug
```

### **Test Connections First**
```bash
./start_app.sh --test-connection --debug
```

### **Production Configuration**
```bash
./start_app.sh \
  --catalog production_catalog \
  --schema healthcare_data \
  --llm-endpoint databricks-claude-3-5-sonnet \
  --port 8080 \
  --host 0.0.0.0
```

## 🌍 Environment Variables

You can also set environment variables directly:

```bash
export HEALTHCARE_CATALOG="my_catalog"
export HEALTHCARE_SCHEMA="payer_silver"
export HEALTHCARE_LLM_ENDPOINT="databricks-meta-llama-3-3-70b-instruct"
export HEALTHCARE_DEBUG="true"

./start_app.sh
```

## 🐳 Docker Support

For containerized deployments:

```bash
# Set environment variables
export HEALTHCARE_CATALOG="my_catalog"
export HEALTHCARE_SCHEMA="payer_silver"
export HEALTHCARE_LLM_ENDPOINT="databricks-meta-llama-3-3-70b-instruct"

# Run with Docker
docker run -e HEALTHCARE_CATALOG -e HEALTHCARE_SCHEMA -e HEALTHCARE_LLM_ENDPOINT \
  -p 8501:8501 healthcare-payor-app
```

## 🔍 Troubleshooting

### **Connection Issues**
```bash
# Test connections before starting
./start_app.sh --test-connection
```

### **Package Issues**
```bash
# Install packages manually
conda run -n azure_databricks pip install databricks-langchain unitycatalog-langchain[databricks] langchain streamlit
```

### **Port Conflicts**
```bash
# Use different port
./start_app.sh --port 8502
```

### **Debug Mode**
```bash
# Enable debug logging
./start_app.sh --debug
```

## 📊 Configuration Validation

The startup script validates:
- ✅ Conda environment exists
- ✅ Databricks CLI connection
- ✅ Required packages installed
- ✅ UC functions accessible
- ✅ LLM endpoint available

## 🚀 Production Deployment

### **Environment-Specific Configurations**

#### **Development**
```bash
./start_app.sh --catalog dev_catalog --schema test_data --debug
```

#### **Staging**
```bash
./start_app.sh --catalog staging_catalog --schema healthcare_data --port 8502
```

#### **Production**
```bash
./start_app.sh \
  --catalog production_catalog \
  --schema healthcare_data \
  --llm-endpoint databricks-claude-3-5-sonnet \
  --port 8080 \
  --host 0.0.0.0
```

## 🔧 Advanced Configuration

### **Custom LLM Endpoints**
```bash
# Use Claude
./start_app.sh --llm-endpoint databricks-claude-3-5-sonnet

# Use Llama
./start_app.sh --llm-endpoint databricks-meta-llama-3-3-70b-instruct

# Use GPT
./start_app.sh --llm-endpoint databricks-gpt-4o
```

### **Temperature Tuning**
```bash
# More creative responses
python start_healthcare_app.py --llm-temperature 0.7

# More deterministic responses
python start_healthcare_app.py --llm-temperature 0.0
```

## 📝 Logging and Monitoring

### **Debug Logging**
```bash
./start_app.sh --debug
```

### **Connection Testing**
```bash
./start_app.sh --test-connection
```

### **Health Checks**
The app includes built-in health checks for:
- Databricks workspace connection
- UC functions availability
- LLM endpoint accessibility
- Required packages installation

## 🎯 Best Practices

1. **Always test connections** before production deployment
2. **Use environment-specific configurations** for different stages
3. **Enable debug mode** for troubleshooting
4. **Monitor resource usage** for LLM endpoints
5. **Keep configurations in version control** for reproducibility

---

**Ready to start your Healthcare Payor AI System! 🏥✨**
